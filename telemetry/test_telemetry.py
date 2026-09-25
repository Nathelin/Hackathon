"""Pruebas de contratos, alertas, API y reconexión real sobre pseudo-terminales."""
import json
import os
import pty
import tempfile
import threading
import time
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api import State, Handler
from bridge import read_port
from domain import SPECS, from_raw, serial_metrics, validate_metrics


def frame(raw=0):
    return {"channels": [{"pin": pin, "raw": raw} for pin in (33, 32, 35, 34)]}


def body(raw=0):
    return {"device_id": "esp32-hydro-1", "simulation": True, "captured_at": time.time(), "metrics": serial_metrics(frame(raw))}


class DomainTests(unittest.TestCase):
    def test_zero_and_pin_mapping(self):
        data = serial_metrics(frame())
        self.assertEqual({k: d['pin'] for k, d in data.items()}, {"ph": 34, "humidity": 33, "ec": 32, "temperature": 35})
        self.assertTrue(all(d['value'] == 0 for d in validate_metrics(data).values()))
        for s in SPECS.values():
            self.assertEqual(from_raw(4095, s), s['maximum'])

    def test_reject_bad_adc_missing_duplicate_and_nan(self):
        for value in (True, -1, 4096, float('nan'), '0'):
            with self.assertRaises(ValueError):
                serial_metrics(frame(value))
        bad = frame()
        bad['channels'][0]['pin'] = 34
        with self.assertRaises(ValueError):
            serial_metrics(bad)
        data = serial_metrics(frame())
        data['ph']['value'] = float('nan')
        with self.assertRaises(ValueError):
            validate_metrics(data)

    def test_threshold_edges(self):
        for key, spec in SPECS.items():
            for value, level in ((sum(spec['normal'])/2, 'safe'), (spec['normal'][0]-.1, 'warning'), (spec['critical'][0]-.1, 'critical'), (spec['critical'][1]+.1, 'critical')):
                data = serial_metrics(frame())
                raw = round(value / spec['maximum'] * 4095)
                data[key].update(raw=raw, value=from_raw(raw, spec))
                self.assertEqual(validate_metrics(data)[key]['level'], level)

    def test_critical_is_immediate_then_reentry_recovery_and_stale(self):
        tick = [0.]
        notifications = []
        state = State(notify=lambda a: notifications.append(a.copy()), clock=lambda: tick[0])
        tick[0] = 0
        state.accept(body())
        self.assertEqual(len(notifications), 4)
        for t in range(1, 8):
            tick[0] = t
            good = body()
            for key, spec in SPECS.items():
                raw = round(sum(spec['normal']) / 2 / spec['maximum'] * 4095)
                good['metrics'][key].update(raw=raw, value=from_raw(raw, spec))
            state.accept(good)
        self.assertTrue(all(a['resolved'] for a in state.events))
        tick[0] = 8
        state.accept(body())
        self.assertEqual(len(notifications), 8)
        for t in range(9, 21):
            tick[0] = t
            state.accept(body())
        self.assertEqual(len(notifications), 8)
        tick[0] = 30
        self.assertFalse(state.snapshot()['connected'])
        state.accept(body())
        self.assertEqual(len(notifications), 8)


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.token = 'test-secret-with-at-least-24-characters'
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, state=self.state, token=self.token))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def post(self, data, token=None):
        req = Request(self.url+'/api/v1/telemetry', data=json.dumps(data).encode(), headers={'Content-Type':'application/json', 'Authorization':'Bearer '+(token or self.token)})
        return urlopen(req, timeout=2)

    def test_auth_validation_and_zero_over_http(self):
        with self.assertRaises(HTTPError) as error:
            self.post(body(), 'bad-token')
        self.assertEqual(error.exception.code, 401)
        error.exception.close()
        bad = body(); bad['tank_id'] = 2
        with self.assertRaises(HTTPError) as error:
            self.post(bad)
        self.assertEqual(error.exception.code, 400)
        error.exception.close()
        good = body()
        with self.post(good) as response:
            self.assertEqual(response.status, 200)
        with self.assertRaises(HTTPError) as error:
            self.post(good)  # captura duplicada
        error.exception.close()
        with urlopen(self.url+'/api/v1/telemetry/latest') as response:
            data = json.load(response)
        self.assertTrue(data['connected'])
        self.assertEqual(data['latest']['metrics']['ph']['value'], 0)


class SerialTests(unittest.TestCase):
    def test_disconnect_reconnect_new_port_and_fragmented_zero(self):
        # Cambiar el destino del mismo symlink reproduce la reenumeración USB.
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / 'esp32'
            for raw in (0, 4095):
                master, slave = pty.openpty()
                os.symlink(os.ttyname(slave), link)
                received, errors = [], []
                started = threading.Event()
                stop = threading.Event()
                def run():
                    try:
                        read_port(str(link), received.append, lambda *_: started.set(), stop, startup=.8, silence=.5)
                    except OSError as error:
                        errors.append(error)
                thread = threading.Thread(target=run)
                thread.start()
                self.assertTrue(started.wait(2))
                os.write(master, b'boot log\nnull\n{"channels":[]}\n')
                line = json.dumps(frame(raw)).encode()+b'\n'
                os.write(master, line[:40]); os.write(master, line[40:])
                deadline = time.monotonic()+1
                while not received and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertEqual(received[0]['metrics']['ph']['value'], 0 if raw == 0 else 14)
                os.close(master)
                thread.join(2)
                self.assertFalse(thread.is_alive())
                self.assertTrue(errors)
                os.close(slave)
                link.unlink()

    def test_continuous_garbage_cannot_keep_connection_alive(self):
        master, slave = pty.openpty()
        done = threading.Event()
        def noise():
            while not done.wait(.02):
                os.write(master, b'x'*200+b'\n')
        thread = threading.Thread(target=noise)
        thread.start()
        try:
            with self.assertRaises(TimeoutError):
                read_port(os.ttyname(slave), lambda _: self.fail('Invalid frame accepted'), lambda *_: None, startup=.3)
        finally:
            done.set(); thread.join(); os.close(master); os.close(slave)


if __name__ == '__main__':
    unittest.main()
