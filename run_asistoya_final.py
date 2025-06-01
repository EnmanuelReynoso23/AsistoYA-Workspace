#!/usr/bin/env python3
"""
🚀 AsistoYA - Ejecutor Principal FINAL
Sistema de Control de Asistencia - VERSIÓN ESTABLE
"""

import sys
import os
from pathlib import Path
import subprocess

def check_and_install_dependencies():
    """Verificar e instalar dependencias críticas"""
    print("📦 Verificando dependencias...")
    
    dependencies = [
        ("opencv-contrib-python", "cv2"),
        ("ttkbootstrap", "ttkbootstrap"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("pillow", "PIL"),
        ("cryptography", "cryptography")
    ]
    
    for package, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"📥 Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} - INSTALADO")

def create_directories():
    """Crear directorios necesarios"""
    print("📁 Verificando directorios...")
    
    directories = [
        "data",
        "faces", 
        "logs",
        "data/auth",
        "data/firebase_sync",
        "data/reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios verificados")

def initialize_data_files():
    """Inicializar archivos de datos básicos"""
    print("📄 Verificando archivos de datos...")
    
    # Archivo de estudiantes
    students_file = Path("data/students.json")
    if not students_file.exists():
        students_file.write_text("[]", encoding="utf-8")
    
    # Archivo de asistencia
    attendance_file = Path("data/attendance.json")
    if not attendance_file.exists():
        attendance_file.write_text("[]", encoding="utf-8")
    
    # Archivo de usuarios
    users_file = Path("data/users.json")
    if not users_file.exists():
        default_users = '''[
    {
        "username": "admin",
        "password": "admin123",
        "full_name": "Administrador",
        "role": "super_admin",
        "email": "admin@asistoya.com",
        "active": true,
        "created_at": "2024-01-01T00:00:00"
    }
]'''
        users_file.write_text(default_users, encoding="utf-8")
    
    # Archivo de configuración
    settings_file = Path("data/settings.json")
    if not settings_file.exists():
        default_settings = '''{
    "recognition_threshold": 70,
    "cooldown_seconds": 10,
    "camera_index": 0,
    "auto_backup": true,
    "firebase_enabled": false
}'''
        settings_file.write_text(default_settings, encoding="utf-8")
    
    print("✅ Archivos de datos verificados")

def run_application():
    """Ejecutar la aplicación principal"""
    print("🚀 Iniciando AsistoYA Enterprise...")
    
    try:
        # Agregar directorio actual al path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Importar y ejecutar
        from asistoya import LoginWindow
        
        print("🏢 Abriendo ventana de login...")
        app = LoginWindow()
        app.run()
        
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🏢 AsistoYA Enterprise - Sistema de Control de Asistencia")
    print("📅 Version 2.0 - FINAL ESTABLE")
    print("=" * 60)
    
    try:
        # 1. Verificar dependencias
        check_and_install_dependencies()
        
        # 2. Crear directorios
        create_directories()
        
        # 3. Inicializar archivos
        initialize_data_files()
        
        # 4. Ejecutar aplicación
        success = run_application()
        
        if success:
            print("✅ Aplicación ejecutada correctamente")
        else:
            print("❌ Error en la ejecución")
            input("Presione Enter para continuar...")
        
    except KeyboardInterrupt:
        print("\n🛑 Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()
