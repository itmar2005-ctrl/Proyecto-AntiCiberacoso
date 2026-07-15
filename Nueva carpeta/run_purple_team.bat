@echo off
chcp 65001 >nul
set "PROJECT_DIR=%~dp0"
set "PYTHON=C:\Users\Usuario\AppData\Local\Programs\Python\Python313\python.exe"

if not exist "%PYTHON%" (
    REM Try py launcher
    where py >nul 2>nul
    if not errorlevel 1 (
        py "%~dp0run.py" %*
        exit /b %errorlevel%
    )
    echo Python no encontrado. Usa la ruta completa:
    echo   C:\ruta\a\python.exe run_purple_team.py --help
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0run.py" %*
