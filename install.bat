@echo off
cd /d "%~dp0"
echo ==========================================
echo       AI COMPANY V1 - INSTALL
echo ==========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=py
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PYTHON_CMD=python
    ) else (
        echo Khong tim thay Python.
        echo Hay cai Python 3.12+ va chon "Add Python to PATH".
        pause
        exit /b 1
    )
)

%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo Tao virtual environment that bai.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo Cai package that bai.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Cai dat thanh cong!
echo Chay run.bat de khoi dong AI Company.
echo ==========================================
pause
