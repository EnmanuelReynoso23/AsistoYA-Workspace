@echo off
title AsistoYA Enterprise - Sistema de Control de Asistencia
echo.
echo ================================================================
echo                 AsistoYA Enterprise v2.0
echo        Sistema de Control de Asistencia con IA
echo ================================================================
echo.
echo 🚀 Iniciando aplicacion...
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no esta instalado
    echo.
    echo Por favor instale Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Ejecutar el script principal
echo 📦 Verificando dependencias e iniciando...
python run_asistoya_final.py

REM Si hay error, mostrar mensaje
if errorlevel 1 (
    echo.
    echo ❌ Error ejecutando la aplicacion
    echo.
    echo Solucion alternativa:
    echo 1. Ejecute: python main.py
    echo 2. O ejecute: python asistoya.py
    echo.
)

echo.
echo Presione cualquier tecla para salir...
pause >nul
