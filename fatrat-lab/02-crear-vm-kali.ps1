#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Crea una VM Kali Linux desde cero en VirtualBox (sin OVA)
.DESCRIPTION
    Alternativa a importar OVA. Descarga ISO y crea VM manualmente.
    Ejecutar en Windows HOST.
#>

$ErrorActionPreference = "Stop"
$LOGDIR = "C:\fatrat-lab-logs"
$LOG = "$LOGDIR\crear-vm-kali.log"
mkdir $LOGDIR -Force -EA 0 | Out-Null

function Log { param($m) "$(Get-Date -Format 'HH:mm:ss') | $m" | Tee-Object $LOG -Append }

Log "=== Creando VM Kali Linux en VirtualBox ==="

# Parametros de la VM
$VM_NAME = "Kali-LAB"
$RAM_MB = 4096
$VRAM_MB = 128
$DISK_MB = 40960  # ~40GB
$CPU = 2

# Ruta VBoxManage
$VBOX = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# 1. Crear la VM
Log "Creando VM '$VM_NAME'..."
& $VBOX createvm --name $VM_NAME --ostype "Debian_64" --register 2>&1 | Out-Null

# 2. Configurar CPU/RAM/Video
Log "Configurando CPU=$CPU RAM=${RAM_MB}MB VRAM=${VRAM_MB}MB..."
& $VBOX modifyvm $VM_NAME --memory $RAM_MB --cpus $CPU --vram $VRAM_MB --graphicscontroller vmsvga --accelerate3d on 2>&1 | Out-Null

# 3. Red: NAT con forwarding para Meterpreter
Log "Configurando red NAT con port forwarding..."
& $VBOX natnetwork add --netname KaliNet --network "192.168.100.0/24" --enable --dhcp on 2>&1 | Out-Null
& $VBOX modifyvm $VM_NAME --nat-network "KaliNet" 2>&1 | Out-Null
& $VBOX setextradata $VM_NAME "VBoxInternal/Devices/pcbios/0/Config/DmiSystemUuid" "11111111-1111-1111-1111-111111111111" 2>&1 | Out-Null

# 4. Disco
Log "Creando disco virtual (${DISK_MB}MB)..."
$DISK_PATH = "$env:USERPROFILE\VirtualBox VMs\$VM_NAME\$VM_NAME.vdi"
& $VBOX createmedium disk --filename $DISK_PATH --size $DISK_MB --variant Standard 2>&1 | Out-Null
& $VBOX storagectl $VM_NAME --name "SATA" --add sata --controller IntelAhci --portcount 1 2>&1 | Out-Null
& $VBOX storageattach $VM_NAME --storagectl "SATA" --port 0 --device 0 --type hdd --medium $DISK_PATH 2>&1 | Out-Null

# 5. DVD (para instalar desde ISO)
$ISO_PATH = "$env:TEMP\kali-linux.iso"
if (!(Test-Path $ISO_PATH)) {
    Log "Descargando Kali ISO (esto tarda)..."
    $url = "https://kali.download/base-images/kali-2024.4/kali-linux-2024.4-installer-amd64.iso"
    Invoke-WebRequest -Uri $url -OutFile $ISO_PATH -UseBasicParsing
    Log "ISO descargada"
}
& $VBOX storagectl $VM_NAME --name "IDE" --add ide --controller PIIX4 2>&1 | Out-Null
& $VBOX storageattach $VM_NAME --storagectl "IDE" --port 0 --device 0 --type dvddrive --medium $ISO_PATH 2>&1 | Out-Null

# 6. Clipboard bidireccional + Drag'n'Drop
& $VBOX modifyvm $VM_NAME --clipboard-mode bidirectional 2>&1 | Out-Null
& $VBOX modifyvm $VM_NAME --draganddrop bidirectional 2>&1 | Out-Null

# 7. Carpeta compartida para pasar scripts
$SHARE_PATH = "C:\Users\Usuario\Documents\1 Semestre 2026\fatrat-lab"
& $VBOX sharedfolder add $VM_NAME --name "fatrat-lab" --hostpath "$SHARE_PATH" --automount 2>&1 | Out-Null

Log ""
Log "=== VM '$VM_NAME' CREADA ==="
Log ""
Log "INSTRUCCIONES:"
Log "  1. Abre VirtualBox > selecciona '$VM_NAME' > Iniciar"
Log "  2. Instala Kali Linux (Graphical Install, todo por defecto)"
Log "  3. Una vez instalado, ejectua en terminal de Kali:"
Log "       sudo mkdir -p /mnt/fatrat-lab"
Log "       sudo mount -t vboxsf fatrat-lab /mnt/fatrat-lab"
Log "       cd /mnt/fatrat-lab"
Log "       bash 03-dentro-kali-setup.sh"
Log ""
Log "  CREDENCIALES POR DEFECTO KALI:  kali / kali"
