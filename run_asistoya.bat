@echo off
chcp 65001 >nul 2>&1
title 🚀 AsistoYA - Sistema de Control de Asistencia

echo.
echo ════════════════════════════════════════════════════════════
echo 🚀 ASISTOYA - SISTEMA ÚNICO DE CONTROL DE ASISTENCIA
echo ════════════════════════════════════════════════════════════
echo.
echo ✅ Tomar asistencia con reconocimiento facial
echo 🆔 Crear códigos de estudiantes
echo 📲 Enviar notificaciones automáticas
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instale Python primero.
    pause
    exit /b 1
)

:: Ejecutar aplicación única
echo 🚀 Iniciando AsistoYA...
echo.
python asistoya.py

echo.
echo 📋 Aplicación finalizada.
pause
