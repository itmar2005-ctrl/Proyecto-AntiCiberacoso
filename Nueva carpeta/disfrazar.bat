@echo off
chcp 65001 >nul
title Disfrazar Call of Duty - Compilador
color 0A
echo ============================================
echo   DISFRAZANDO ARCHIVO COMO CALL OF DUTY
echo ============================================
echo.
echo [1/4] Generando icono de Call of Duty...
py -3.13 generar_icono_cod.py
if %errorlevel% neq 0 (
    echo [!] Pillow no encontrado. Instalando...
    py -3.13 -m pip install pillow
    py -3.13 generar_icono_cod.py
)

if not exist cod_icon.ico (
    echo [x] No se pudo crear el icono
    pause
    exit /b 1
)

echo [2/4] Instalando PyInstaller...
py -3.13 -m pip install pyinstaller

echo [3/4] Compilando .EXE (esto tarda 1-2 min)...
py -3.13 -m PyInstaller --onefile --noconsole ^
    --icon=cod_icon.ico ^
    --name "Call of Duty Black Ops VI" ^
    --version-file nul ^
    "Call of Duty Black Ops VI.py"

echo [4/4] Eliminando rastros...
if exist "dist\Call of Duty Black Ops VI.exe" (
    echo.
    echo ============================================
    echo  LISTO! Archivo creado:
    echo  %CD%\dist\Call of Duty Black Ops VI.exe
    echo.
    echo  Icono: Call of Duty (naranja/negro)
    echo  Sin consola, sin logo Python
    echo ============================================
    start "" "%CD%\dist"
) else (
    echo [x] Error en compilacion. Ejecuta manualmente:
    echo   py -3.13 -m PyInstaller --onefile --noconsole --icon=cod_icon.ico --name "Call of Duty Black Ops VI" "Call of Duty Black Ops VI.py"
)

echo.
echo Para limpiar archivos temporales:
echo   rmdir /s /q build __pycache__
echo   del /q "Call of Duty Black Ops VI.spec"
echo.
pause
