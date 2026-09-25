"""Pruebas del analizador local: combinaciones, foco y API sin Internet."""
import json
import time
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import test_telemetry
from ai_chat import Chat, ChatError, analyze
from api import Handler, State
from domain import SPECS, from_raw, serial_metrics


SAFE_RAW = {'ph': 1697, 'humidity': 2457, 'ec': 1228, 'temperature': 1956}


def snapshot_with(raw_by_key):
    state = State()
    metrics = serial_metrics({'channels': [
        {'pin': spec['pin'], 'raw': raw_by_key.get(key, SAFE_RAW[key])}
        for key, spec in SPECS.items()
    ]})
    state.accept({'device_id': 'esp32-hydro-1', 'simulation': True,
                  'captured_at': time.time(), 'metrics': metrics})
    return state.snapshot()


class LocalAnalysisTests(unittest.TestCase):
    def test_all_safe_gives_positive_feedback_and_all_values(self):
        reply = analyze(snapshot_with({}), 'Analizá todo')
        self.assertIn('cuatro lecturas están dentro del objetivo', reply)
        for spec in SPECS.values():
            self.assertIn(spec['label'], reply)
        self.assertIn('condición simulada es favorable', reply)

    def test_multiple_bad_states_are_all_reported_and_safe_is_reinforced(self):
        # pH bajo crítico, EC baja en advertencia, temperatura alta crítica, humedad segura.
        reply = analyze(snapshot_with({'ph': 0, 'ec': 819, 'temperature': 3185}), 'riesgos actuales')
        self.assertIn('2 parámetros en nivel crítico y 1 que necesita atención', reply)
        self.assertIn('⚠ pH de la solución', reply)
        self.assertIn('! Conductividad', reply)
        self.assertIn('⚠ Temperatura del aire', reply)
        self.assertIn('Lo que está bien: Humedad del aire', reply)
        self.assertIn('pH y conductividad están fuera del objetivo al mismo tiempo', reply)

    def test_combined_environment_condition(self):
        reply = analyze(snapshot_with({'humidity': 819, 'temperature': 3185}), 'visión general')
        self.assertIn('Temperatura alta y humedad baja aparecen juntas', reply)

    def test_question_focus_uses_current_server_data_and_mentions_other_risks(self):
        snapshot = snapshot_with({'ph': 0, 'temperature': 3185})
        reply = Chat().ask({'message': '¿Cómo está el pH?', 'history': [],
                            'metrics': {'ph': {'value': 6}}}, snapshot)['reply']
        self.assertIn('pH de la solución: 0,00 pH', reply)
        self.assertNotIn('Humedad del aire:', reply)
        self.assertIn('otros valores para revisar: Temperatura del aire', reply)

    def test_disconnected_does_not_describe_old_values_as_current(self):
        snapshot = snapshot_with({})
        snapshot['connected'] = False
        reply = analyze(snapshot, '¿Está todo bien?')
        self.assertIn('no tiene una lectura vigente', reply)
        self.assertNotIn('condición simulada es favorable', reply)

    def test_config_needs_no_key_and_validation_is_bounded(self):
        chat = Chat()
        config = chat.config()
        self.assertTrue(config['configured'])
        self.assertFalse(config['external_api'])
        self.assertEqual(config['cost'], 0)
        for body in ([], {'message': ''}, {'message': 'x'*1201},
                     {'message': 'OK', 'history': [{'role': 'system', 'content': 'x'}]},
                     {'message': 'OK', 'history': [{}]*7}):
            with self.subTest(body=str(body)[:50]), self.assertRaises(ChatError):
                chat.ask(body, snapshot_with({}))


class LocalAnalysisHTTPTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.state.accept(test_telemetry.body())
        self.token = 'test-secret-with-at-least-24-characters'
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, state=self.state, token=self.token))
        import threading
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def query(self, token=None, origin=None):
        headers = {'Content-Type': 'application/json',
                   'X-Hydro-Chat-Token': token or self.state.chat.token}
        if origin:
            headers['Origin'] = origin
        request = Request(self.url+'/api/v1/ai/chat', data=b'{"message":"Analizar todo","history":[]}', headers=headers)
        return urlopen(request, timeout=2)

    def test_config_and_chat_work_without_external_credentials(self):
        with urlopen(self.url+'/api/v1/ai/config') as response:
            config = json.load(response)
        self.assertTrue(config['configured'])
        self.assertFalse(config['external_api'])
        with self.query() as response:
            body = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertIn('4 parámetros en nivel crítico', body['reply'])
        self.assertEqual(body['usage']['total_tokens'], 0)

    def test_csrf_and_origin_protection_remain(self):
        for token, origin in [('wrong', None), (None, 'https://evil.example')]:
            with self.assertRaises(HTTPError) as caught:
                self.query(token, origin)
            self.assertEqual(caught.exception.code, 403)
            caught.exception.close()


if __name__ == '__main__':
    unittest.main()
