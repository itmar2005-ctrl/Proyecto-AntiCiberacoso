#Requires -RunAsAdministrator
<#
.SYNOPSIS
    INICIO RAPIDO - LABORATORIO FATRAT
.EXAMPLE
    .\start-lab.ps1                  # Menu interactivo
    .\start-lab.ps1 -Mode docker     # Solo Docker
    .\start-lab.ps1 -Mode vm         # Solo VM (VirtualBox)
    .\start-lab.ps1 -Mode help       # Ayuda
#>

param(
    [ValidateSet("menu","docker","vm","help")]
    [string]$Mode = "menu"
)

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$LOGDIR = "C:\fatrat-lab-logs"
mkdir $LOGDIR -Force -EA 0 | Out-Null

function Show-Banner {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       LABORATORIO THEFATRAT - CONTROL CENTER    ║" -ForegroundColor Cyan
    Write-Host "╠══════════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "║  Scripts en:         $ROOT  ║" -ForegroundColor Cyan
    Write-Host "║  Logs:               $LOGDIR        ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║              GUIA RAPIDA DE ARCHIVOS                      ║
╚═══════════════════════════════════════════════════════════╝

📁 ESTRUCTURA:
$(Split-Path -Path $ROOT -Leaf)\
├── 00-LEEME-PRIMERO.txt       ← LEER PRIMERO
├── 01-instalar-virtualbox.ps1 ← Windows: Instala VirtualBox
├── 02-crear-vm-kali.ps1       ← Windows: Crea VM Kali
├── 03-dentro-kali-setup.sh    ← Kali VM: Setup completo
├── 04-docker-compose.yml      ← Windows: Docker alternativo
├── 05-docker-setup.sh         ← Docker: Setup interno
├── 06-alternativas-modernas.sh← Kali: Herramientas 2026
├── 07-generar-payload-ejemplo.sh ← Kali: Demo rapida
├── 08-windows-victima-config.ps1 ← Win Victima: Config
├── start-lab.ps1              ← Este script
├── Dockerfile.fatrat          ← Docker image
├── scripts/
│   ├── msfvenom-plus          ← Wrapper payload
│   └── listener.rc            ← Template listener
└── output/                    ← Payloads generados

🌐 DONDE EJECUTAR CADA COSA:

┌─────────────────────┬──────────────────────┬──────────────────────────┐
│ SCRIPT              │ DONDE                │ COMO                     │
├─────────────────────┼──────────────────────┼──────────────────────────┤
│ 01-*.ps1            │ Windows HOST (Admin) │ .\01-*.ps1               │
│ 02-*.ps1            │ Windows HOST (Admin) │ .\02-*.ps1               │
│ 03-*.sh             │ Kali VM              │ sudo bash 03-*.sh        │
│ docker-compose.yml  │ Windows HOST         │ docker-compose -f up -d  │
│ 05-*.sh             │ Docker container     │ bash /scripts/05-*.sh    │
│ 06-*.sh             │ Kali VM              │ sudo bash 06-*.sh        │
│ 07-*.sh             │ Kali VM              │ sudo bash 07-*.sh <IP>   │
│ 08-*.ps1            │ Win Victima (Admin)  │ .\08-*.ps1               │
└─────────────────────┴──────────────────────┴──────────────────────────┘

🔥 COMANDOS UTILES:

  # Ver logs en tiempo real (Kali)
  tail -f /tmp/fatrat-lab/*.log

  # Ver resumen final (Kali)
  cat /tmp/fatrat-lab/resumen-final.txt

  # Compartir carpeta Windows <-> Kali
  En VirtualBox: Dispositivos > Carpeta Compartida > fatrat-lab

  # Copiar payloads a Windows Victima
  scp ~/payloads/*.exe usuario@victima:C:\payloads\

"@
}

function Show-Menu {
    Show-Banner
    Write-Host "SELECCIONA UNA OPCION:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1]  LEER GUIA RAPIDA (recomendado)"
    Write-Host "  [2]  Instalar VirtualBox + Extension Pack"
    Write-Host "  [3]  Crear VM Kali Linux en VirtualBox"
    Write-Host "  [4]  Iniciar con Docker (alternativa rapida)"
    Write-Host "  [5]  Mostrar comandos rapidos"
    Write-Host "  [6]  SALIR"
    Write-Host ""
    $opt = Read-Host "Opcion [1-6]"

    switch ($opt) {
        "1" { Show-Help; pause; Show-Menu }
        "2" { & "$ROOT\01-instalar-virtualbox.ps1"; pause; Show-Menu }
        "3" { & "$ROOT\02-crear-vm-kali.ps1"; pause; Show-Menu }
        "4" {
            Write-Host ""
            Write-Host "[DOCKER] Comandos:" -ForegroundColor Green
            Write-Host "  docker-compose -f `"$ROOT\04-docker-compose.yml`" up -d fatrat"
            Write-Host "  docker exec -it fatrat-container bash /scripts/05-docker-setup.sh"
            Write-Host "  docker exec -it fatrat-container bash /scripts/07-generar-payload-ejemplo.sh"
            pause; Show-Menu
        }
        "5" { Show-Help; pause; Show-Menu }
        "6" { exit }
        default { Show-Menu }
    }
}

switch ($Mode) {
    "menu"  { Show-Menu }
    "docker" { 
        Write-Host "[DOCKER] Iniciando..."
        docker-compose -f "$ROOT\04-docker-compose.yml" up -d fatrat
    }
    "vm" { 
        & "$ROOT\02-crear-vm-kali.ps1"
    }
    "help" { Show-Help }
}
