@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Chua co moi truong Python. Hay chay install.bat truoc.
    pause
    exit /b 1
)
echo.
echo ==========================================
echo       AI COMPANY V1.0.0
echo ==========================================
echo.
echo Mo trinh duyet tai: http://127.0.0.1:8000
echo Nhan CTRL+C de dung server.
echo.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
