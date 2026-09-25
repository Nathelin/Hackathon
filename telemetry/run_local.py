#!/usr/bin/env python3
"""Inicia API y lector; reinicia cada hijo si falla y los cierra al terminar."""
import logging
import os
from pathlib import Path
import secrets
import shlex
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent


def load_config():
    path = ROOT / 'config.env'
    if not path.exists():
        # Secreto generado localmente, nunca embebido en Vue ni en el repositorio.
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, 'w') as stream:
                stream.write('HYDRO_API_TOKEN=' + secrets.token_urlsafe(32) + '\n')
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, sep, value = line.partition('=')
        if not sep:
            raise ValueError('Línea inválida en config.env')
        parts = shlex.split(value, comments=True)
        os.environ.setdefault(key.strip(), ' '.join(parts))


def main():
    load_config()
    logging.basicConfig(level=logging.INFO)
    if not (ROOT.parent / 'dashboard' / 'dist' / 'index.html').exists():
        raise SystemExit('Primero ejecutá npm run build en dashboard/')
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    children = {}
    try:
        while not stop.is_set():
            for name in ('api.py', 'bridge.py'):
                if name not in children or children[name].poll() is not None:
                    logging.info('Iniciando %s', name)
                    children[name] = subprocess.Popen([sys.executable, str(ROOT / name)], cwd=ROOT)
            stop.wait(2)
    finally:
        for child in children.values():
            if child.poll() is None:
                child.terminate()
        for child in children.values():
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == '__main__':
    main()
