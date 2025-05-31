#!/usr/bin/env python
"""
Test rápido para AsistoYA Enterprise
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Probar que todos los imports funcionen"""
    try:
        print("🔍 Probando imports...")
        
        from auth.authentication import get_auth_manager
        print("✅ auth.authentication - OK")
        
        from firebase.firebase_config import get_firebase
        print("✅ firebase.firebase_config - OK")
        
        from ui.modern_dashboard import ModernDashboard
        print("✅ ui.modern_dashboard - OK")
        
        from models.student_model import student_model
        print("✅ models.student_model - OK")
        
        from models.attendance_model import attendance_model
        print("✅ models.attendance_model - OK")
        
        from reports.advanced_reports import get_report_generator
        print("✅ reports.advanced_reports - OK")
        
        from models.user_model import user_model
        print("✅ models.user_model - OK")
        
        print("\n🎉 Todos los imports funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_auth():
    """Probar autenticación"""
    try:
        print("\n🔍 Probando autenticación...")
        
        from auth.authentication import get_auth_manager
        auth = get_auth_manager()
        
        # Probar autenticación con credenciales por defecto
        user = auth.authenticate("admin", "admin123")
        
        if user:
            print(f"✅ Autenticación exitosa: {user['full_name']} ({user['role']})")
            return True
        else:
            print("❌ Fallo en autenticación")
            return False
            
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False

def test_student_model():
    """Probar modelo de estudiantes"""
    try:
        print("\n🔍 Probando modelo de estudiantes...")
        
        from models.student_model import student_model
        
        # Probar obtener estudiantes
        students = student_model.get_all_students()
        print(f"✅ Estudiantes obtenidos: {len(students)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelo de estudiantes: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests de AsistoYA Enterprise...")
    
    tests = [
        test_imports,
        test_auth,
        test_student_model
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error ejecutando test {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Resultados:")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    
    if failed == 0:
        print("\n🎉 ¡Todos los tests pasaron! La aplicación está lista.")
        print("\n🚀 Para ejecutar la aplicación:")
        print("python asistoya_enterprise.py")
        print("\n🔑 Credenciales:")
        print("Usuario: admin")
        print("Contraseña: admin123")
    else:
        print(f"\n⚠️ {failed} tests fallaron. Revise los errores arriba.")

if __name__ == "__main__":
    main()
