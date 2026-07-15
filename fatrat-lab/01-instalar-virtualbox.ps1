#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Instala VirtualBox + Extension Pack + descarga Kali Linux VM
.DESCRIPTION
    Ejecutar en Windows HOST como ADMINISTRADOR
    Esto configura todo lo necesario para correr Kali Linux en VM
.NOTES
    Salida: C:\fatrat-lab-logs\setup-virtualbox.log
#>

$ErrorActionPreference = "Stop"
$LOGDIR  = "C:\fatrat-lab-logs"
$LOG     = "$LOGDIR\setup-virtualbox.log"
mkdir $LOGDIR -Force -ErrorAction SilentlyContinue | Out-Null

function Write-Log { param([string]$Msg) $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"; "$timestamp | $Msg" | Tee-Object -FilePath $LOG -Append }

Write-Log "=== INICIO: Instalacion VirtualBox ==="

# 1. Detectar version de Windows (x64 / arm64)
$ARCH = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
$WINVER = [Environment]::OSVersion.Version.Major
Write-Log "Windows $WINVER | Arquitectura: $ARCH"

# 2. Verificar si VirtualBox ya esta instalado
$vb = Get-ItemProperty "HKLM:\SOFTWARE\Oracle\VirtualBox" -ErrorAction SilentlyContinue
if ($vb) {
    Write-Log "VirtualBox ya instalado: $($vb.Version)"
} else {
    Write-Log "Descargando VirtualBox 7.0+..."
    $url = "https://download.virtualbox.org/virtualbox/7.0.20/VirtualBox-7.0.20-167901-Win.exe"
    $out = "$env:TEMP\VirtualBox.exe"
    Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
    Write-Log "Instalando VirtualBox (silencioso)..."
    Start-Process -FilePath $out -ArgumentList "--silent --ignore-reboot" -Wait -NoNewWindow
    Write-Log "VirtualBox instalado. (Reinicia si pide)"
}

# 3. Extension Pack
$extVer = "7.0.20"
$extFile = "$env:TEMP\Oracle_VM_VirtualBox_Extension_Pack-$extVer.vbox-extpack"
if (!(Test-Path $extFile)) {
    Write-Log "Descargando Extension Pack..."
    Invoke-WebRequest -Uri "https://download.virtualbox.org/virtualbox/$extVer/Oracle_VM_VirtualBox_Extension_Pack-$extVer.vbox-extpack" -OutFile $extFile -UseBasicParsing
}
Write-Log "Instalando Extension Pack (acepta licencia automaticamente)..."
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" extpack install --accept-license $extFile 2>&1 | Out-Null
Write-Log "Extension Pack OK"

# 4. Descargar Kali Linux VM (OVA prebuild oficial)
$kaliOva = "$env:TEMP\kali-linux.ova"
$kaliUrl = "https://kali.download/base-images/kali-2024.4/kali-linux-2024.4-virtualbox-amd64.7z"
if (!(Test-Path $kaliOva)) {
    Write-Log "Descargando Kali Linux VM (OVA) - esto puede tardar..."
    Write-Log "URL: $kaliUrl"
    # Nota: requiere 7z para extraer. Si no tienes, usamos curl
    Invoke-WebRequest -Uri $kaliUrl -OutFile "$env:TEMP\kali.7z" -UseBasicParsing
    Write-Log "Descarga completa. Extrae el .ova con 7-Zip manualmente, o usa:"
    Write-Log "  7z x $env:TEMP\kali.7z -o$env:TEMP\"
}
Write-Log "Alternativa: descarga manual desde https://www.kali.org/get-kali/#kali-virtual-machines"
Write-Log "Importa el .ova en VirtualBox: Archivo > Importar Servicio Virtualizado"

# 5. Configurar red NAT para la VM
Write-Log "Configurando red NAT en VirtualBox..."
try {
    & "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" natnetwork add --netname KaliNet --network "192.168.100.0/24" --enable --dhcp on 2>&1 | Out-Null
} catch {
    Write-Log "Red NAT ya existe o error (no critico): $_"
}

Write-Log "=== FIN: Instalacion VirtualBox ==="
Write-Log ""
Write-Log "PROXIMO PASO:"
Write-Log "  1. Abre VirtualBox"
Write-Log "  2. Archivo > Importar Servicio Virtualizado > selecciona el .ova"
Write-Log "  3. Inicia la VM de Kali"
Write-Log "  4. Dentro de Kali, ejecuta: bash /scripts/03-dentro-kali-setup.sh"
Write-Log "     (copia los scripts a Kali con USB o carpeta compartida)"
