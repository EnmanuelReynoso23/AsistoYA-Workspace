#!/usr/bin/env python3
"""
🚀 AsistoYA - Sistema de Control de Asistencia
Punto de entrada principal de la aplicación
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Función principal de la aplicación"""
    try:
        print("🚀 Iniciando AsistoYA...")
        print("📦 Verificando dependencias...")
        
        # Verificar dependencias críticas
        try:
            import cv2
            print("✅ OpenCV instalado")
        except ImportError:
            print("❌ OpenCV no encontrado. Instalando...")
            os.system("pip install opencv-contrib-python")
            import cv2
            
        try:
            import ttkbootstrap
            print("✅ ttkbootstrap instalado")
        except ImportError:
            print("❌ ttkbootstrap no encontrado. Instalando...")
            os.system("pip install ttkbootstrap")
            import ttkbootstrap
        
        # Verificar si existe asistoya.py
        if (current_dir / "asistoya.py").exists():
            print("🏢 Iniciando AsistoYA Enterprise...")
            from asistoya import LoginWindow
            
            # Crear y ejecutar aplicación enterprise
            app = LoginWindow()
            app.run()
            
        elif (current_dir / "face_attendance_system.py").exists():
            print("📱 Iniciando AsistoYA Standard...")
            import tkinter as tk
            import ttkbootstrap as ttk
            from face_attendance_system import AdvancedAttendanceApp
            
            # Crear y ejecutar aplicación standard
            root = ttk.Window(themename="cosmo")
            app = AdvancedAttendanceApp(root)
            root.mainloop()
            
        else:
            print("❌ No se encontraron archivos de aplicación")
            print("Busque: asistoya.py o face_attendance_system.py")
            return False
            
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("Presione Enter para salir...")
        sys.exit(1)
