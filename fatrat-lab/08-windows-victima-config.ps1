#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Configura una VM Windows 10/11 como VICTIMA para pruebas
.DESCRIPTION
    - Desactiva Windows Defender temporalmente (SOLO LABORATORIO)
    - Crea excepciones para la carpeta de payloads
    - Configura reglas de firewall para permitir conexiones entrantes
    - Instala herramientas de monitoreo (Process Monitor, TCPView)

    EJECUTAR EN LA VM VICTIMA (NO EN TU HOST PRINCIPAL)
.NOTES
    SOLO PARA LABORATORIO AISLADO - NUNCA EN PRODUCCION
#>

$ErrorActionPreference = "Stop"
$LOG = "$env:TEMP\victima-setup.log"
$PAYLOAD_DIR = "C:\payloads"

function Log { param([string]$M) "$(Get-Date -Format 'HH:mm:ss') | $M" | Out-File -FilePath $LOG -Append; Write-Host "[*] $M" }

# Verificar que no estamos en un host de produccion
$computerName = $env:COMPUTERNAME
if ($computerName -notmatch "VICTIMA|LAB|TEST|WIN10|WIN11") {
    Write-Warning "Esta maquina parece ser de produccion ($computerName). ¿Continuar?"
    $continue = Read-Host "Escribe 'SI' para continuar"
    if ($continue -ne "SI") { exit }
}

Log "=== Configurando VM Victima ==="

# 1. Crear directorio de payloads
mkdir $PAYLOAD_DIR -Force -EA 0
Log "Directorio: $PAYLOAD_DIR"

# 2. Desactivar Windows Defender (SOLO LABORATORIO!)
Log "Desactivando Windows Defender (SOLO LAB)..."
Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableBehaviorMonitoring $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableBlockAtFirstSeen $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableIOAVProtection $true -ErrorAction SilentlyContinue
Add-MpPreference -ExclusionPath $PAYLOAD_DIR -ErrorAction SilentlyContinue
Log "Defender desactivado (solo para este laboratorio)"

# 3. Firewall: permitir conexiones entrantes
Log "Configurando Firewall..."
New-NetFirewallRule -DisplayName "LAB-Meterpreter" -Direction Inbound -Protocol TCP -LocalPort 4444-4450 -Action Allow -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "LAB-Meterpreter-Out" -Direction Outbound -Protocol TCP -LocalPort 4444-4450 -Action Allow -ErrorAction SilentlyContinue | Out-Null
Log "Firewall: puertos 4444-4450 abiertos"

# 4. Desactivar SmartScreen
Log "Desactivando SmartScreen..."
Set-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "SmartScreenEnabled" -Value "Off" -Type String -Force -ErrorAction SilentlyContinue
Log "SmartScreen desactivado"

# 5. Desactivar UAC (para pruebas)
Log "Desactivando UAC (SOLO LAB)..."
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Log "UAC desactivado (requiere reinicio)"

# 6. Descargar herramientas de monitoreo
Log "Descargando herramientas de monitoreo..."
$tools = @{
    "procexp64.exe"  = "https://download.sysinternals.com/files/ProcessExplorer.zip"
    "tcpview64.exe"  = "https://download.sysinternals.com/files/TCPView.zip"
    "procmon64.exe"  = "https://download.sysinternals.com/files/ProcessMonitor.zip"
}
$toolDir = "$PAYLOAD_DIR\tools"
mkdir $toolDir -Force -EA 0 | Out-Null

foreach ($tool in $tools.Keys) {
    $zipPath = "$env:TEMP\$tool.zip"
    try {
        Invoke-WebRequest -Uri $tools[$tool] -OutFile $zipPath -UseBasicParsing -ErrorAction SilentlyContinue
        Expand-Archive -Path $zipPath -DestinationPath $toolDir -Force -ErrorAction SilentlyContinue
        Log "    $tool descargado"
    } catch {
        Log "    $tool: no se pudo descargar (sin internet?)"
    }
}

# 7. Mensaje final
Log ""
Log "======================================"
Log "VM VICTIMA CONFIGURADA"
Log "======================================"
Log ""
Log "DIRECTORIO PAYLOADS: $PAYLOAD_DIR"
Log "HERRAMIENTAS:       $toolDir"
Log ""
Log "INSTRUCCIONES:"
Log "  1. REINICIA LA VM (necesario para UAC)"
Log "  2. Copia los payloads a $PAYLOAD_DIR"
Log "     (desde Kali: scp kali@<IP_KALI>:~/payloads/*.exe .)"
Log "  3. Ejecuta el payload manualmente"
Log "  4. Monitorea con: $toolDir\procexp64.exe"
Log "  5. Ver conexiones: $toolDir\tcpview64.exe"
Log ""
Log "LOG: $LOG"
