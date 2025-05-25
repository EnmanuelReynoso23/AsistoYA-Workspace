@echo off
echo ========================================
echo     AsistoYA - Sistema de Asistencia
echo ========================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo Error: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo.
echo Verificando dependencias...
python -c "import cv2, numpy, PIL, pandas, tkinter; print('Dependencias basicas OK')"
if errorlevel 1 (
    echo.
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo.
echo Iniciando AsistoYA...
echo Presione Ctrl+C para detener la aplicacion
echo.

python main_app.py

if errorlevel 1 (
    echo.
    echo Error: La aplicacion se cerro inesperadamente
    pause
)

echo.
echo Aplicacion cerrada correctamente
pause
