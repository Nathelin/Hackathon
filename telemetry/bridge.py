#!/usr/bin/env python3
"""ESP32 USB → POST REST. Linux, Python estándar; reconexión sin reiniciar la web."""
import array
import errno
import fcntl
import json
import logging
import os
from pathlib import Path
import queue
import select
import signal
import termios
import threading
import time
from urllib.request import Request, urlopen
from urllib.error import URLError

from domain import serial_metrics

STOP = threading.Event()
USB_NAME = "usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0"


def find_port():
    # Identidad del adaptador conocido. No se sondean otros equipos seriales.
    target = Path(os.getenv("HYDRO_SERIAL", "/dev/serial/by-id/" + USB_NAME))
    return str(target) if target.exists() else None


def open_serial(path):
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.ioctl(fd, termios.TIOCEXCL)
        attrs = termios.tcgetattr(fd)
        attrs[0], attrs[1], attrs[3] = termios.IGNPAR, 0, 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[4] = attrs[5] = termios.B115200
        # No heredar VMIN/VTIME, paridad, CRTSCTS o HUPCL de otra aplicación.
        attrs[6][termios.VMIN], attrs[6][termios.VTIME] = 0, 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        # Liberar EN/BOOT: no mantener el ESP32 en reset por RTS/DTR.
        try:
            fcntl.ioctl(fd, termios.TIOCMBIC, array.array('i', [termios.TIOCM_DTR | termios.TIOCM_RTS]))
        except OSError as error:
            if error.errno != errno.ENOTTY:  # PTY de pruebas sin líneas de módem.
                raise
        termios.tcflush(fd, termios.TCIFLUSH)
        return fd
    except BaseException:
        close_serial(fd)
        raise


def close_serial(fd):
    try:
        fcntl.ioctl(fd, termios.TIOCNXCL)
    except OSError:
        pass
    os.close(fd)


class Publisher:
    """El HTTP nunca bloquea la lectura USB; cola acotada, sin replay de datos viejos."""
    def __init__(self, url, token):
        self.url, self.token = url.rstrip('/'), token
        self.jobs = queue.Queue(maxsize=32)
        self.dropped = 0
        self.thread = threading.Thread(target=self.send_forever, daemon=True)
        self.thread.start()

    def put(self, path, payload):
        job = (path, payload, time.monotonic())
        try:
            self.jobs.put_nowait(job)
        except queue.Full:
            try:
                self.jobs.get_nowait()
            except queue.Empty:
                pass
            self.dropped += 1
            self.jobs.put_nowait(job)

    def send_forever(self):
        last_error = -1e9
        while not STOP.is_set():
            try:
                path, payload, created = self.jobs.get(timeout=.5)
            except queue.Empty:
                continue
            if time.monotonic()-created > 3:
                continue
            try:
                req = Request(self.url + path, data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.token}, method="POST")
                with urlopen(req, timeout=2) as response:
                    response.read(1024)
            except (URLError, OSError) as error:
                if time.monotonic()-last_error > 10:
                    logging.warning("API no disponible (%s); se retomará con nuevas lecturas", error)
                    last_error = time.monotonic()
                STOP.wait(.5)


def read_port(path, emit, status, stop=STOP, startup=6., silence=3.):
    fd = open_serial(path)
    try:
        identity = os.fstat(fd)
        status("opening", "ESP32 detectado; iniciando recepción", os.path.realpath(path))
        deadline = time.monotonic() + startup
        heartbeat = 0.
        received = False
        buffer = b''
        while not stop.is_set():
            now = time.monotonic()
            # El plazo depende de tramas válidas, nunca del mero ruido recibido.
            if now >= deadline:
                raise TimeoutError("Sin tramas válidas; revisando conexión y firmware")
            current = os.stat(path)
            if (current.st_ino, current.st_rdev) != (identity.st_ino, identity.st_rdev):
                raise OSError("El USB fue reemplazado; reabriendo")
            if now-heartbeat >= 2:
                status("receiving" if received else "opening", "Telemetría en vivo" if received else "Esperando datos del firmware", os.path.realpath(path))
                heartbeat = now
            ready, _, _ = select.select([fd], [], [], min(.25, deadline-now))
            if not ready:
                continue
            try:
                chunk = os.read(fd, 4096)
            except BlockingIOError:
                continue
            if not chunk:
                raise OSError("ESP32 desconectado")
            buffer += chunk
            lines = buffer.split(b'\n')
            buffer = lines.pop()
            if len(buffer) > 8192:
                buffer = b''
            for line in lines:
                if len(line) > 8192:
                    continue
                try:
                    metrics = serial_metrics(json.loads(line))
                except (ValueError, TypeError, UnicodeDecodeError):
                    continue
                if not received:
                    logging.info("Cuatro canales reconocidos en %s", os.path.realpath(path))
                    status("receiving", "Telemetría en vivo", os.path.realpath(path))
                received = True
                deadline = time.monotonic() + silence
                emit({"device_id": "esp32-hydro-1", "greenhouse_id": 1, "tank_id": 1,
                      "simulation": True, "captured_at": time.time(), "metrics": metrics})
    finally:
        close_serial(fd)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    token = os.getenv("HYDRO_API_TOKEN", "")
    if len(token) < 24:
        raise SystemExit("Configurar HYDRO_API_TOKEN")
    publisher = Publisher(os.getenv("HYDRO_API_URL", "http://127.0.0.1:8080"), token)
    def status(value, reason, port=""):
        publisher.put("/api/v1/bridge/status", {"status": value, "reason": reason, "port": port})
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: STOP.set())
    retry = .5
    last_message = ""
    while not STOP.is_set():
        path = find_port()
        if path is None:
            status("searching", "ESP32 desconectado; conectá el USB")
            STOP.wait(.5)
            continue
        try:
            read_port(path, lambda body: publisher.put("/api/v1/telemetry", body), status)
            retry = .5
        except (OSError, ValueError, termios.error) as error:
            message = str(error)
            status("error", message, os.path.realpath(path))
            if message != last_message:
                logging.warning("Serial: %s", message)
                last_message = message
            STOP.wait(retry)
            retry = min(3., retry*1.5)


if __name__ == "__main__":
    main()
