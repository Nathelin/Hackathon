"""Prueba integral: proceso bridge real + REST + USB virtual intercambiable."""
import json
import os
from pathlib import Path
import pty
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from functools import partial
from http.server import ThreadingHTTPServer

from api import Handler, State


class ReconnectionTest(unittest.TestCase):
    def test_bridge_recovers_after_unplug_and_api_restart(self):
        token = 'integration-secret-at-least-24-characters'
        state = State()
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, state=state, token=token))
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        sender_stop = threading.Event()
        devices = []
        def wait_for(predicate, seconds=10):
            until = time.monotonic()+seconds
            while time.monotonic() < until:
                if predicate():
                    return
                time.sleep(.05)
            self.fail('No se recuperó la telemetría dentro del plazo')
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / 'device'
            def plug(raw):
                master, slave = pty.openpty()
                devices.extend([master, slave])
                link.symlink_to(os.ttyname(slave))
                def send():
                    line = json.dumps({'channels': [{'pin': p, 'raw': raw} for p in (34, 33, 32, 35)]}).encode()+b'\n'
                    while not sender_stop.wait(.15):
                        try:
                            os.write(master, line)
                        except OSError:
                            return
                writer = threading.Thread(target=send)
                writer.start()
                return master, writer
            master, writer = plug(0)
            process = subprocess.Popen([sys.executable, str(Path(__file__).with_name('bridge.py'))],
                env={**os.environ, 'HYDRO_SERIAL': str(link), 'HYDRO_API_URL': f'http://127.0.0.1:{port}', 'HYDRO_API_TOKEN': token},
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                wait_for(lambda: state.snapshot()['connected'])
                self.assertEqual(state.snapshot()['latest']['metrics']['ph']['value'], 0)
                sender_stop.set(); writer.join(); link.unlink(); os.close(master); devices.remove(master)
                wait_for(lambda: not state.snapshot()['connected'])
                sender_stop.clear()
                master, writer = plug(4095)
                wait_for(lambda: state.snapshot()['connected'] and state.snapshot()['latest']['metrics']['ph']['value'] == 14)
                # Cortar la API no detiene la recepción serial. Vuelve con datos nuevos.
                server.shutdown(); server.server_close(); thread.join()
                time.sleep(.8)
                state = State()
                server = ThreadingHTTPServer(('127.0.0.1', port), partial(Handler, state=state, token=token))
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                wait_for(lambda: state.snapshot()['connected'])
                self.assertEqual(state.snapshot()['latest']['metrics']['humidity']['value'], 100)
                self.assertIsNone(process.poll())
            finally:
                process.terminate(); process.wait(timeout=5)
                sender_stop.set(); writer.join(timeout=2)
                for fd in devices:
                    os.close(fd)
                server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
