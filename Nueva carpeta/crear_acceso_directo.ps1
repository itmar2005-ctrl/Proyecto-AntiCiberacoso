# Crea un acceso directo en el escritorio con icono de Call of Duty
$wsh = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$target = "$PSScriptRoot\Call of Duty Black Ops VI.pyw"
$shortcut = $wsh.CreateShortcut("$desktop\Call of Duty Black Ops VI.lnk")
$shortcut.TargetPath = "C:\Users\Usuario\AppData\Local\Programs\Python\Python313\pythonw.exe"
$shortcut.Arguments = "`"$target`""
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = "Call of Duty Black Ops VI"
# Si existe el .ico, usarlo
$iconPath = "$PSScriptRoot\cod_icon.ico"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath, 0"
}
$shortcut.Save()
Write-Host "[OK] Acceso directo creado en el escritorio"
