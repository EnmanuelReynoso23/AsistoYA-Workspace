@echo off
echo ========================================
echo   AsistoYA - Verificacion del Sistema
echo ========================================
echo.

echo Ejecutando verificacion completa...
echo.

python verificar_sistema.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   VERIFICACION FALLO
    echo ========================================
    echo.
    echo Algunas pruebas no pasaron. Revise los errores arriba.
    echo.
    echo Acciones recomendadas:
    echo 1. Instalar dependencias: pip install -r requirements.txt
    echo 2. Verificar que Python 3.8+ este instalado
    echo 3. Instalar OpenCV: pip install opencv-contrib-python
    echo.
) else (
    echo.
    echo ========================================
    echo   VERIFICACION EXITOSA
    echo ========================================
    echo.
    echo El sistema esta listo para usar!
    echo Para ejecutar AsistoYA: run_app.bat
    echo.
)

pause
