#!/usr/bin/env python3
"""
AsistoYA - Verificación Completa del Sistema
Script mejorado para verificar todas las funcionalidades
"""

import sys
import os
from datetime import datetime

def print_header(title):
    """Imprimir encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step, description):
    """Imprimir paso de verificación"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def test_python_version():
    """Verificar versión de Python"""
    print_step("1", "VERIFICANDO VERSIÓN DE PYTHON")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requiere Python 3.8+")
        return False

def test_opencv():
    """Verificar OpenCV y sus funcionalidades"""
    print_step("2", "VERIFICANDO OPENCV Y RECONOCIMIENTO FACIAL")
    
    try:
        import cv2
        print(f"✅ OpenCV instalado: {cv2.__version__}")
        
        # Verificar Haar Cascade
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(cascade_path)
        
        if cascade.empty():
            print("❌ Error: Haar Cascade no disponible")
            return False
        else:
            print("✅ Haar Cascade para detección facial: Disponible")
        
        # Verificar LBPH Face Recognizer
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            print("✅ LBPH Face Recognizer: Disponible")
        except AttributeError:
            print("❌ LBPH Face Recognizer: No disponible")
            print("   Instale: pip install opencv-contrib-python")
            return False
        
        # Verificar acceso a cámara
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print("✅ Cámara: Accesible y funcionando")
                    
                    # Probar detección de rostros
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = cascade.detectMultiScale(gray, 1.3, 5)
                    print(f"✅ Detección facial: {len(faces)} rostro(s) detectado(s)")
                else:
                    print("⚠️  Cámara: Accesible pero sin frames")
                cap.release()
            else:
                print("⚠️  Cámara: No disponible (normal si no hay cámara)")
        except Exception as e:
            print(f"⚠️  Cámara: Error - {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando OpenCV: {e}")
        print("   Instale: pip install opencv-contrib-python")
        return False

def test_dependencies():
    """Verificar dependencias adicionales"""
    print_step("3", "VERIFICANDO DEPENDENCIAS ADICIONALES")
    
    dependencies = [
        ("numpy", "Procesamiento numérico"),
        ("PIL", "Manipulación de imágenes (Pillow)"),
        ("pandas", "Análisis de datos"),
        ("matplotlib", "Visualización"),
        ("tkinter", "Interfaz gráfica")
    ]
    
    all_ok = True
    
    for dep, desc in dependencies:
        try:
            if dep == "PIL":
                import PIL
                version = getattr(PIL, '__version__', 'desconocida')
            elif dep == "tkinter":
                import tkinter as tk
                # Probar crear ventana
                root = tk.Tk()
                root.withdraw()  # Ocultar ventana
                root.destroy()
                version = tk.TkVersion
            else:
                module = __import__(dep)
                version = getattr(module, '__version__', 'desconocida')
            
            print(f"✅ {dep}: {version} - {desc}")
            
        except ImportError:
            print(f"❌ {dep}: No instalado - {desc}")
            all_ok = False
            
            # Sugerir instalación
            if dep == "PIL":
                print("   Instale: pip install Pillow")
            elif dep == "tkinter":
                print("   Tkinter debería estar incluido con Python")
            else:
                print(f"   Instale: pip install {dep}")
    
    return all_ok

def test_file_structure():
    """Verificar estructura de archivos"""
    print_step("4", "VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    
    required_files = [
        ("main_app.py", "Aplicación principal"),
        ("requirements.txt", "Lista de dependencias"),
        ("README.md", "Documentación"),
        ("PROYECTO_LIMPIO.md", "Estado del proyecto")
    ]
    
    optional_files = [
        ("verificar_sistema.py", "Este script de verificación"),
        ("face_attendance_system.py", "Sistema anterior (marcado obsoleto)")
    ]
    
    all_present = True
    
    print("Archivos requeridos:")
    for file, desc in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: Presente ({size} bytes) - {desc}")
        else:
            print(f"❌ {file}: Faltante - {desc}")
            all_present = False
    
    print("\nArchivos opcionales:")
    for file, desc in optional_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: Presente ({size} bytes) - {desc}")
        else:
            print(f"⚠️  {file}: No presente - {desc}")
    
    # Verificar directorios
    print("\nDirectorios:")
    directories = ["faces", "data", "reports"]
    
    for directory in directories:
        if os.path.exists(directory):
            files_count = len(os.listdir(directory))
            print(f"✅ {directory}/: Presente ({files_count} archivos)")
        else:
            print(f"⚠️  {directory}/: Será creado automáticamente")
    
    return all_present

def test_main_application():
    """Probar importación de la aplicación principal"""
    print_step("5", "PROBANDO APLICACIÓN PRINCIPAL")
    
    try:
        # Intentar importar sin ejecutar la GUI
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_app", "main_app.py")
        
        if spec is None:
            print("❌ No se pudo cargar main_app.py")
            return False
        
        module = importlib.util.module_from_spec(spec)
        
        # Verificar que se puede cargar el módulo
        spec.loader.exec_module(module)
        print("✅ main_app.py: Importación exitosa")
        
        # Verificar clases principales
        if hasattr(module, 'AsistoYASystem'):
            print("✅ AsistoYASystem: Clase disponible")
        else:
            print("❌ AsistoYASystem: Clase no encontrada")
            return False
        
        if hasattr(module, 'AsistoYAGUI'):
            print("✅ AsistoYAGUI: Clase disponible")
        else:
            print("❌ AsistoYAGUI: Clase no encontrada")
            return False
        
        # Intentar instanciar el sistema (sin GUI)
        try:
            system = module.AsistoYASystem()
            stats = system.get_statistics()
            print(f"✅ Sistema instanciado: {stats['total_students']} estudiantes registrados")
            return True
        except Exception as e:
            print(f"❌ Error instanciando sistema: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error cargando aplicación: {e}")
        return False

def run_performance_test():
    """Ejecutar prueba básica de rendimiento"""
    print_step("6", "PRUEBA DE RENDIMIENTO BÁSICA")
    
    try:
        import cv2
        import numpy as np
        import time
        
        # Crear imagen de prueba
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Probar conversión a escala de grises
        start_time = time.time()
        for _ in range(100):
            gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        gray_time = time.time() - start_time
        
        print(f"✅ Conversión a escala de grises: {gray_time:.3f}s (100 iteraciones)")
        
        # Probar detección de rostros
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        start_time = time.time()
        for _ in range(10):
            faces = cascade.detectMultiScale(gray, 1.3, 5)
        detection_time = time.time() - start_time
        
        print(f"✅ Detección facial: {detection_time:.3f}s (10 iteraciones)")
        
        # Evaluar rendimiento
        if gray_time < 1.0 and detection_time < 2.0:
            print("✅ Rendimiento: Excelente")
        elif gray_time < 2.0 and detection_time < 5.0:
            print("✅ Rendimiento: Bueno")
        else:
            print("⚠️  Rendimiento: Puede ser lento en hardware modesto")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de rendimiento: {e}")
        return False

def generate_report(results):
    """Generar reporte final"""
    print_header("REPORTE FINAL DE VERIFICACIÓN")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Pruebas ejecutadas: {total_tests}")
    print(f"Pruebas exitosas: {passed_tests}")
    print(f"Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetalle de resultados:")
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {status} - {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡VERIFICACIÓN COMPLETADA EXITOSAMENTE!")
        print("✅ AsistoYA está listo para usar")
        print("\n🚀 Para ejecutar la aplicación:")
        print("   python main_app.py")
        
        print("\n📋 INSTRUCCIONES DE USO:")
        print("1. Ejecute: python main_app.py")
        print("2. Vaya a la pestaña 'Estudiantes'")
        print("3. Registre algunos estudiantes")
        print("4. Use la pestaña 'Reconocimiento' para iniciar el sistema")
        print("5. Exporte reportes desde la pestaña 'Dashboard'")
        
    else:
        print(f"\n⚠️  VERIFICACIÓN INCOMPLETA: {total_tests - passed_tests} prueba(s) fallaron")
        print("\n🔧 ACCIONES RECOMENDADAS:")
        
        if not results.get("Dependencias"):
            print("• Instale dependencias: pip install -r requirements.txt")
        
        if not results.get("OpenCV"):
            print("• Instale OpenCV: pip install opencv-contrib-python")
        
        if not results.get("Aplicación"):
            print("• Revise el archivo main_app.py")
        
        print("\n• Ejecute este script nuevamente después de las correcciones")

def main():
    """Función principal de verificación"""
    print_header("ASISTOYA - VERIFICACIÓN COMPLETA DEL SISTEMA")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Este script verificará que AsistoYA esté completamente funcional")
    
    # Ejecutar todas las pruebas
    results = {}
    
    results["Versión Python"] = test_python_version()
    results["OpenCV"] = test_opencv()
    results["Dependencias"] = test_dependencies()
    results["Estructura de archivos"] = test_file_structure()
    results["Aplicación"] = test_main_application()
    results["Rendimiento"] = run_performance_test()
    
    # Generar reporte final
    generate_report(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado durante la verificación: {e}")
        sys.exit(1)
