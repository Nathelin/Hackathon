#!/usr/bin/env python3
"""API REST local + archivos del dashboard compilado. Estado acotado en memoria."""
import copy
import hmac
import json
import logging
import os
import queue
import smtplib
import ssl
import threading
import time
import uuid
from collections import deque
from email.message import EmailMessage
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from domain import PROFILE, SPECS, validate_metrics
from ai_chat import Chat, ChatError

ROOT = Path(__file__).resolve().parents[1]
STALE = 4.0
CONFIRM = 0.0
RECOVER = 5.0
COOLDOWN = 0.0


class State:
    def __init__(self, notify=lambda event: None, clock=time.monotonic):
        self.lock = threading.RLock()
        self.clock, self.notify = clock, notify
        self.latest = None
        self.last_at = None
        self.received = 0
        self.history = deque(maxlen=120)
        self.events = deque(maxlen=100)
        self.alerts = {}
        self.bridge = {"status": "waiting", "reason": "Esperando el lector serial"}
        self.bridge_at = None
        self.last_history = -1e9
        self.chat = Chat()

    def accept(self, body):
        if not isinstance(body, dict):
            raise ValueError("Se espera un objeto JSON")
        if body.get("greenhouse_id", 1) != 1 or body.get("tank_id", 1) != 1:
            raise ValueError("Este prototipo admite Invernadero 1 / Tanque 1")
        if body.get("device_id") != "esp32-hydro-1" or body.get("simulation") is not True:
            raise ValueError("Identidad o modo de simulación inválidos")
        captured = body.get("captured_at")
        if type(captured) not in (int, float) or not 0 <= time.time() - captured <= 15:
            raise ValueError("La captura debe tener menos de 15 segundos")
        metrics = validate_metrics(body.get("metrics"))
        now = self.clock()
        with self.lock:
            if self.latest and captured <= self.latest["captured_at"]:
                raise ValueError("Captura duplicada o fuera de orden")
            if self.last_at is not None and now - self.last_at > STALE:
                self.reset_pending()
            self.latest = {"metrics": metrics, "captured_at": captured, "received_at": time.time()}
            self.last_at = now
            self.received += 1
            if now-self.last_history >= 1:
                self.history.append({"at": captured, "values": {k: m["value"] for k, m in metrics.items()}})
                self.last_history = now
            self.evaluate(metrics, now)

    def reset_pending(self):
        for alert in self.alerts.values():
            alert["since"] = None
            alert["recovery"] = None

    def evaluate(self, metrics, now):
        for key, metric in metrics.items():
            a = self.alerts.setdefault(key, {"since": None, "active": False, "recovery": None, "last_sent": -1e9, "direction": None})
            if metric["level"] == "critical":
                a["recovery"] = None
                if a["direction"] != metric["direction"]:
                    a["since"] = None
                a["direction"] = metric["direction"]
                if a["since"] is None:
                    a["since"] = now
                if now-a["since"] >= CONFIRM and not a["active"] and now-a["last_sent"] >= COOLDOWN:
                    a["active"], a["last_sent"] = True, now
                    event = {"id": str(uuid.uuid4()), "metric": key, "label": SPECS[key]["label"],
                             "value": metric["value"], "unit": SPECS[key]["unit"], "at": time.time(),
                             "message": metric["advice"], "email": "disabled", "resolved": False}
                    self.events.appendleft(event)
                    self.notify(event)
            else:
                a["since"] = None
                if a["active"]:
                    if a["recovery"] is None:
                        a["recovery"] = now
                    if now-a["recovery"] >= RECOVER:
                        a["active"] = False
                        for e in self.events:
                            if e["metric"] == key:
                                e["resolved"] = True

    def bridge_status(self, body):
        if not isinstance(body, dict) or body.get("status") not in ("searching", "opening", "receiving", "error"):
            raise ValueError("Estado del lector inválido")
        with self.lock:
            self.bridge = {k: str(body.get(k, ""))[:300] for k in ("status", "reason", "port")}
            self.bridge_at = self.clock()
            if body["status"] != "receiving":
                self.last_at = None
                self.reset_pending()

    def snapshot(self):
        with self.lock:
            now = self.clock()
            age = None if self.last_at is None else now-self.last_at
            connected = age is not None and age <= STALE
            bridge = dict(self.bridge)
            if self.bridge_at is None or now-self.bridge_at > 8:
                bridge = {"status": "offline", "reason": "Lector sin señal reciente; verificá el servicio local", "port": ""}
            elif not connected and bridge.get("status") == "receiving":
                bridge["reason"] = "No hay lecturas recientes; esperando recuperación del ESP32"
            return copy.deepcopy({"connected": connected, "age_seconds": age,
                "greenhouse_id": 1, "tank_id": 1, "simulation": True, "profile": PROFILE,
                "specs": SPECS, "latest": self.latest, "received": self.received,
                "history": list(self.history), "alerts": list(self.events), "bridge": bridge,
                "email_configured": bool(os.getenv("SMTP_HOST") and os.getenv("ALERT_EMAIL_TO")),
                "alert_confirmation_seconds": CONFIRM})


class Mailer:
    def __init__(self, state):
        self.state = state
        self.jobs = queue.Queue(maxsize=16)
        threading.Thread(target=self.work, daemon=True).start()

    def enqueue(self, event):
        if not (os.getenv("SMTP_HOST") and os.getenv("ALERT_EMAIL_TO")):
            return
        event["email"] = "queued"
        try:
            self.jobs.put_nowait(event.copy())
        except queue.Full:
            event["email"] = "failed"

    def work(self):
        while True:
            event = self.jobs.get()
            status = "sent"
            try:
                msg = EmailMessage()
                msg["Subject"] = f"[SIMULACIÓN] Alerta: {event['label']} · Invernadero 1 / Tanque 1"
                msg["From"] = os.environ["SMTP_FROM"]
                msg["To"] = os.environ["ALERT_EMAIL_TO"]
                msg.set_content(f"Valor simulado: {event['value']} {event['unit']}\n{event['message']}\nVerificá en el dashboard. No es una medición real del cultivo.")
                with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "587")), timeout=8) as client:
                    client.starttls(context=ssl.create_default_context())
                    if os.getenv("SMTP_USER"):
                        client.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
                    client.send_message(msg)
            except Exception:
                logging.exception("No se pudo enviar la alerta por correo")
                status = "failed"
            with self.state.lock:
                for item in self.state.events:
                    if item["id"] == event["id"]:
                        item["email"] = status
            self.jobs.task_done()


class Handler(SimpleHTTPRequestHandler):
    def local_ui_request(self):
        # El prototipo sólo escucha en loopback. Evita peticiones de otros sitios
        # al endpoint con costo, incluyendo Host de un dominio externo.
        host = urlsplit('http://' + self.headers.get('Host', '')).hostname
        origin = self.headers.get('Origin')
        return host in ('localhost', '127.0.0.1', '::1') and (
            origin is None or urlsplit(origin).hostname in ('localhost', '127.0.0.1', '::1'))

    def __init__(self, *args, state, token, **kwargs):
        self.state, self.token = state, token
        super().__init__(*args, directory=str(ROOT / "dashboard" / "dist"), **kwargs)

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def json_response(self, status, payload):
        content = json.dumps(payload, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/v1/ai/config':
            if not self.local_ui_request():
                return self.json_response(403, {'error': 'Sólo disponible desde la interfaz local'})
            return self.json_response(200, self.state.chat.config())
        if path in ("/api/v1/telemetry/latest", "/api/data", "/api/health"):
            return self.json_response(200, self.state.snapshot())
        if path.startswith("/api/"):
            return self.json_response(404, {"error": "Ruta inexistente"})
        resolved = Path(self.translate_path(path))
        if not resolved.is_file():
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == '/api/v1/ai/chat':
            return self.chat_request()
        if not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + self.token):
            return self.json_response(401, {"error": "Token de ingestión inválido"})
        path = urlsplit(self.path).path
        if path not in ("/api/v1/telemetry", "/api/v1/bridge/status"):
            return self.json_response(404, {"error": "Ruta inexistente"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                return self.json_response(413, {"error": "JSON vacío o mayor a 16 KB"})
            if self.headers.get_content_type() != "application/json":
                return self.json_response(415, {"error": "Usar application/json"})
            body = json.loads(self.rfile.read(size))
            if path == "/api/v1/telemetry":
                self.state.accept(body)
            else:
                self.state.bridge_status(body)
        except (ValueError, TypeError, KeyError) as error:
            return self.json_response(400, {"error": str(error)})
        return self.json_response(200, {"accepted": True})

    def chat_request(self):
        if not self.local_ui_request() or not hmac.compare_digest(self.headers.get('X-Hydro-Chat-Token', ''), self.state.chat.token):
            return self.json_response(403, {'error': 'Sesión de chat vencida. Cerrá y volvé a abrir el chat.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 32768:
                return self.json_response(413, {'error': 'Consulta demasiado grande'})
            if self.headers.get_content_type() != 'application/json':
                return self.json_response(415, {'error': 'Usar application/json'})
            body = json.loads(self.rfile.read(size))
            result = self.state.chat.ask(body, self.state.snapshot())
        except ChatError as error:
            return self.json_response(error.status, {'error': str(error)})
        except (ValueError, TypeError):
            return self.json_response(400, {'error': 'Consulta inválida'})
        return self.json_response(200, result)

    def log_message(self, fmt, *args):
        if args and str(args[1]) not in ("200", "304"):
            logging.info(fmt, *args)


def main():
    logging.basicConfig(level=logging.INFO)
    token = os.environ.get("HYDRO_API_TOKEN", "")
    if len(token) < 24:
        raise SystemExit("Configurar HYDRO_API_TOKEN con al menos 24 caracteres")
    state = State()
    state.notify = Mailer(state).enqueue
    server = ThreadingHTTPServer(("127.0.0.1", int(os.getenv("HYDRO_PORT", "8080"))), partial(Handler, state=state, token=token))
    logging.info("Dashboard + API local listos en http://127.0.0.1:%s", server.server_port)
    server.serve_forever()


if __name__ == "__main__":
    main()
