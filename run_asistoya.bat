@echo off
echo.
echo =========================================
echo    AsistoYA - Sistema de Asistencia
echo    con Reconocimiento Facial y 
echo    Notificaciones a Padres
echo =========================================
echo.

echo 🚀 Iniciando AsistoYA...
echo.

echo 📋 Verificando dependencias...
python -c "import cv2, ttkbootstrap, numpy, PIL, pandas, matplotlib" 2>nul
if errorlevel 1 (
    echo ❌ Faltan dependencias. Instalando...
    pip install opencv-python ttkbootstrap numpy pillow pandas matplotlib seaborn
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

echo ✅ Dependencias verificadas
echo.

echo 🎥 Iniciando aplicación principal...
echo.
echo 📱 Funciones disponibles:
echo    • Registro de estudiantes con reconocimiento facial
echo    • Detección automática de asistencia
echo    • Notificaciones a padres vía Firebase
echo    • Portal web para padres: http://localhost:5000
echo.
echo 💡 Para usar el portal de padres:
echo    1. Registre un estudiante con datos de padre/madre
echo    2. Use el token generado en: http://localhost:5000
echo.

python face_attendance_system.py

if errorlevel 1 (
    echo.
    echo ❌ Error ejecutando la aplicación
    echo 💡 Verifique que la cámara esté conectada
    pause
)

echo.
echo 👋 AsistoYA cerrado
pause
