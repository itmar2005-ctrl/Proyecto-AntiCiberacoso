@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "PROJECT_DIR=C:\Users\Usuario\Documents\1 Semestre 2026\Nueva carpeta"
set "PYTHON=C:\Users\Usuario\AppData\Local\Programs\Python\Python313\python.exe"

echo ============================================
echo   Purple Team Framework v2.0
echo   Professional Cybersecurity Platform
echo ============================================
echo.

REM Verificar que el modulo purple_team existe
if not exist "%PROJECT_DIR%\purple_team" (
    echo ERROR: No se encuentra purple_team en %PROJECT_DIR%
    pause
    exit /b 1
)

REM Intentar con python.exe directo
if exist "%PYTHON%" (
    "%PYTHON%" -c "import sys; sys.path.insert(0, r'%PROJECT_DIR%'); from purple_team.__main__ import main; main()" %*
    exit /b !errorlevel!
)

REM Fallback con py launcher
where py >nul 2>nul
if not errorlevel 1 (
    py -c "import sys; sys.path.insert(0, r'%PROJECT_DIR%'); from purple_team.__main__ import main; main()" %*
    exit /b !errorlevel!
)

echo ERROR: Python no encontrado
pause
exit /b 1
