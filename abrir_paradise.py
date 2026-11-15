"""Inicia el servidor local y abre Hotel Paradise cuando esté disponible."""

import argparse
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


def puerto_disponible(inicial):
    for puerto in range(inicial, min(inicial + 20, 65536)):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', puerto))
            except OSError:
                continue
            return puerto
    raise RuntimeError('No se encontró un puerto local libre.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('puerto', type=int, nargs='?', default=8000)
    args = parser.parse_args()
    if not 1024 <= args.puerto <= 65535:
        parser.error('El puerto debe estar entre 1024 y 65535.')

    puerto = puerto_disponible(args.puerto)
    url = f'http://127.0.0.1:{puerto}/'
    print(f'Hotel Paradise: {url}', flush=True)
    print('Mantén esta ventana abierta. Presiona Ctrl+C para cerrar.', flush=True)
    servidor = subprocess.Popen(
        [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{puerto}', '--noreload'],
        cwd=Path(__file__).resolve().parent,
    )
    try:
        limite = time.monotonic() + 30
        while time.monotonic() < limite:
            if servidor.poll() is not None:
                return servidor.returncode or 1
            try:
                with urllib.request.urlopen(url, timeout=1) as respuesta:
                    if respuesta.status == 200 and b'Hotel Paradise' in respuesta.read():
                        break
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(0.25)
        else:
            print(f'No se pudo iniciar Hotel Paradise en {url}.', file=sys.stderr)
            return 1

        try:
            if not webbrowser.open(url):
                print(f'Abre manualmente {url} en tu navegador.', flush=True)
        except Exception:
            print(f'Abre manualmente {url} en tu navegador.', flush=True)
        return servidor.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        if servidor.poll() is None:
            servidor.terminate()
            try:
                servidor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                servidor.kill()
                servidor.wait()


if __name__ == '__main__':
    sys.exit(main())
