@echo off
echo ================================================
echo 🏢 ASISTOYA ENTERPRISE EDITION LAUNCHER
echo ================================================
echo.
echo 🚀 Iniciando AsistoYA Enterprise...
echo 📦 Sistema de Control de Asistencia Profesional
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado
    echo 📥 Descargue Python desde: https://python.org
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Crear directorios necesarios
if not exist "data\auth" mkdir "data\auth"
if not exist "logs" mkdir "logs"
if not exist "reports" mkdir "reports"

echo 📁 Directorios verificados
echo.

REM Instalar dependencias si es necesario
echo 📦 Verificando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ⚠️ Advertencia: Algunas dependencias podrían faltar
    echo 💡 Ejecute manualmente: pip install -r requirements.txt
)

echo ✅ Dependencias verificadas
echo.

REM Ejecutar aplicación empresarial
echo 🏢 Iniciando AsistoYA Enterprise Edition...
echo.
echo ============================================
echo   CREDENCIALES POR DEFECTO:
echo   👤 Usuario: admin
echo   🔑 Contraseña: admin123
echo ============================================
echo.

python asistoya_enterprise.py

if errorlevel 1 (
    echo.
    echo ❌ Error ejecutando la aplicación
    echo 💡 Verifique que todas las dependencias estén instaladas
    echo 💡 Ejecute: pip install -r requirements.txt
    pause
)
