@echo off
cd /d "C:\Users\Usuario\Documents\1 Semestre 2026\CyberAI\backend"
C:\Users\Usuario\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn app.main:app --reload --port 8080
pause
