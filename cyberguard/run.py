"""
CyberGuard - Protector contra Ciberacoso
=========================================
Aplicación web para detección de discurso malicioso y ciberacoso usando NLP.

Uso:
    python run.py

Esto inicia el servidor en http://localhost:8000
"""

import subprocess
import sys
import os
import webbrowser
import time


def main():
    print("""
    ╔══════════════════════════════════════════════╗
    ║           CyberGuard v1.0                    ║
    ║  Detección de discurso malicioso usando NLP  ║
    ╚══════════════════════════════════════════════╝

    [*] Iniciando CyberGuard API...
    [*] Abriendo http://localhost:8000 en tu navegador
    [*] Presiona CTRL+C para detener

    """)

    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0",
             "--port", "8000", "--reload"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )

        time.sleep(2)
        webbrowser.open("http://localhost:8000")
        proc.wait()

    except KeyboardInterrupt:
        print("\n[*] CyberGuard detenido")
        proc.terminate()
    except FileNotFoundError:
        print("[!] Error: uvicorn no encontrado")
        print("[*] Instala las dependencias con:")
        print("    pip install -r backend/requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
