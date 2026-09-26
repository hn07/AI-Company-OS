@echo off
title AI Company OS - Ollama Setup

echo ==========================================
echo AI Company OS - Ollama Local AI Setup
echo ==========================================
echo.

where ollama >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Khong tim thay lenh "ollama".
    echo Hay cai Ollama truoc, sau do mo lai file nay.
    pause
    exit /b 1
)

echo [1/3] Kiem tra Ollama...
ollama --version
if errorlevel 1 (
    echo [ERROR] Ollama khong san sang.
    pause
    exit /b 1
)

echo.
echo [2/3] Tai model qwen2.5:7b...
ollama pull qwen2.5:7b
if errorlevel 1 (
    echo [ERROR] Khong tai duoc model.
    pause
    exit /b 1
)

echo.
echo [3/3] Kiem tra model...
ollama list

echo.
echo HOAN TAT.
echo Tao .env tu .env.example va dat LLM_PROVIDER=ollama.
pause
