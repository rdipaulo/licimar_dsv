@echo off
REM Quick Start Script for Licimar MVP on Windows
REM Run: start.bat

setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║   LICIMAR MVP - Quick Start (Windows)                ║
echo ╚══════════════════════════════════════════════════════╝
echo.

echo Iniciando Backend (Python/Flask)...
echo.

REM Get current directory
for /f "delims=" %%A in ('cd') do set PROJ_DIR=%%A

REM Start Backend in new window
start "Licimar Backend - Python Flask" cmd /k "cd /d "%PROJ_DIR%\backend\licimar_mvp_app" && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Frontend in new window
echo Iniciando Frontend (React/Vite)...
start "Licimar Frontend - React Vite" cmd /k "cd /d "%PROJ_DIR%\frontend\licimar_mvp_frontend" && npm run dev -- --host"

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║ ✓ Aplicação iniciada em 2 terminais!                 ║
echo ║                                                       ║
echo ║ Frontend: http://localhost:5173                      ║
echo ║ Backend:  http://localhost:5000                      ║
echo ║                                                       ║
echo ║ Credenciais de Teste:                                ║
echo ║  - Admin: admin / admin123                           ║
echo ║  - Operador: operador / operador123                  ║
echo ╚══════════════════════════════════════════════════════╝
echo.

pause
