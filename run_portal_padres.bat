@echo off
echo.
echo =========================================
echo    AsistoYA - Portal Web para Padres
echo =========================================
echo.

echo 🌐 Iniciando portal web para padres...
echo.

echo 📋 Verificando dependencias...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ❌ Flask no encontrado. Instalando...
    pip install flask
    if errorlevel 1 (
        echo ❌ Error instalando Flask
        pause
        exit /b 1
    )
)

echo ✅ Dependencias verificadas
echo.

echo 🚀 Portal web disponible en:
echo    👉 http://localhost:5000
echo    👉 http://127.0.0.1:5000
echo.
echo 💡 Los padres pueden usar su token para ver la asistencia
echo 💡 Presione Ctrl+C para detener el servidor
echo.

python parent_portal.py

if errorlevel 1 (
    echo.
    echo ❌ Error ejecutando el portal
    pause
)

echo.
echo 👋 Portal cerrado
pause
