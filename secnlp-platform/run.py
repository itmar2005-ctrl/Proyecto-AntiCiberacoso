"""
Script para ejecutar SecNLP Platform
"""
import subprocess
import sys
import os
import webbrowser
import time

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print(r"""
    ╔═══════════════════════════════════════════════╗
    ║           SecNLP Platform v2.0                ║
    ║  Motor de Moderación de Lenguaje Natural      ║
    ║  Detección de Discurso Malicioso y Ciberacoso ║
    ╚═══════════════════════════════════════════════╝

    [*] Iniciando servidor en http://localhost:8000
    [*] Documentación API: http://localhost:8000/docs
    [*] Dashboard:        http://localhost:8000
    [*] Presiona CTRL+C para detener
    """)

    os.environ["PYTHONPATH"] = BACKEND_DIR

    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=BACKEND_DIR,
        )

        time.sleep(3)
        webbrowser.open("http://localhost:8000")
        proc.wait()

    except KeyboardInterrupt:
        print("\n[*] SecNLP Platform detenido")
        proc.terminate()
    except FileNotFoundError:
        print("[!] Error: uvicorn no encontrado")
        print("[*] Instala las dependencias:")
        print(f"    {sys.executable} -m pip install -r backend/requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
