"""
🔥 Ejemplo de Integración Firebase con AsistoYA
Demostración de cómo usar la nueva configuración Firebase en AsistoYA
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Importar la nueva integración Firebase
try:
    from firebase_integration import (
        get_integration, 
        save_attendance, 
        register_student, 
        get_attendance_records,
        sync_to_firebase
    )
    FIREBASE_AVAILABLE = True
    print("✅ Firebase Integration cargada correctamente")
except ImportError as e:
    print(f"⚠️ Firebase Integration no disponible: {e}")
    FIREBASE_AVAILABLE = False

class AsistoYAFirebaseExample:
    """Ejemplo de integración Firebase con AsistoYA"""
    
    def __init__(self):
        self.firebase_integration = get_integration() if FIREBASE_AVAILABLE else None
        self.data_dir = Path(__file__).parent / "data"
        
    def ejemplo_registro_estudiante(self):
        """Ejemplo de cómo registrar un estudiante con Firebase"""
        print("\n🧑‍🎓 Ejemplo: Registro de Estudiante")
        print("-" * 40)
        
        # Datos de ejemplo de un estudiante
        estudiante_data = {
            'id': 'ER001',
            'student_id': 'ER001',  # Compatibilidad con formato existente
            'name': 'Enmanuel Reynoso',
            'nombre': 'Enmanuel Reynoso',  # Compatibilidad
            'email': 'enmanuel.reynoso@estudiante.com',
            'phone': '+1-809-555-0123',
            'grade': '12vo',
            'curso': '12vo',  # Compatibilidad
            'classroom': 'Aula 301',
            'aula': 'Aula 301',  # Compatibilidad
            'face_encoding': [0.1, 0.2, 0.3],  # Simulado
            'registration_date': datetime.now().isoformat()
        }
        
        if FIREBASE_AVAILABLE:
            # Registrar usando la nueva integración
            success = register_student(estudiante_data)
            if success:
                print(f"✅ Estudiante registrado: {estudiante_data['name']}")
                return True
            else:
                print(f"❌ Error registrando estudiante")
                return False
        else:
            # Fallback manual si Firebase no está disponible
            return self._registro_local_estudiante(estudiante_data)
    
    def ejemplo_registro_asistencia(self):
        """Ejemplo de cómo registrar asistencia con Firebase"""
        print("\n📝 Ejemplo: Registro de Asistencia")
        print("-" * 40)
        
        # Datos del estudiante (como vendría del reconocimiento facial)
        estudiante_detectado = {
            'id': 'ER001',
            'student_id': 'ER001',
            'name': 'Enmanuel Reynoso',
            'student_name': 'Enmanuel Reynoso',
            'grade': '12vo',
            'classroom': 'Aula 301'
        }
        
        # Información de la detección facial
        deteccion_info = {
            'confidence': 0.94,
            'method': 'face_recognition_opencv',
            'detection_time': datetime.now().isoformat(),
            'camera_id': 'CAM_001',
            'coordinates': {'x': 150, 'y': 200, 'w': 100, 'h': 120}
        }
        
        if FIREBASE_AVAILABLE:
            # Guardar usando la nueva integración
            success = save_attendance(estudiante_detectado, deteccion_info)
            if success:
                print(f"✅ Asistencia registrada: {estudiante_detectado['name']}")
                print(f"   Confianza: {deteccion_info['confidence']:.2%}")
                return True
            else:
                print(f"❌ Error registrando asistencia")
                return False
        else:
            # Fallback manual si Firebase no está disponible
            return self._registro_local_asistencia(estudiante_detectado, deteccion_info)
    
    def ejemplo_consulta_registros(self):
        """Ejemplo de cómo consultar registros con Firebase"""
        print("\n📊 Ejemplo: Consulta de Registros")
        print("-" * 40)
        
        if not FIREBASE_AVAILABLE:
            print("⚠️ Firebase no disponible para consultas")
            return
        
        try:
            # Obtener todos los registros
            todos_registros = get_attendance_records()
            print(f"📋 Total de registros: {len(todos_registros)}")
            
            # Filtrar por fecha actual
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            registros_hoy = get_attendance_records({'date': fecha_hoy})
            print(f"📅 Registros de hoy: {len(registros_hoy)}")
            
            # Filtrar por estudiante específico
            registros_estudiante = get_attendance_records({'student_id': 'ER001'})
            print(f"🧑‍🎓 Registros de ER001: {len(registros_estudiante)}")
            
            # Mostrar últimos 3 registros
            if todos_registros:
                print("\n📝 Últimos registros:")
                for i, registro in enumerate(todos_registros[-3:], 1):
                    print(f"   {i}. {registro.get('student_name', 'N/A')} - {registro.get('timestamp', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ Error consultando registros: {e}")
    
    def ejemplo_reporte_diario(self):
        """Ejemplo de cómo generar un reporte diario"""
        print("\n📈 Ejemplo: Reporte Diario")
        print("-" * 40)
        
        if not FIREBASE_AVAILABLE:
            print("⚠️ Firebase no disponible para reportes")
            return
        
        try:
            integration = get_integration()
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            
            # Generar reporte del día
            reporte = integration.create_daily_report(fecha_hoy)
            
            if reporte:
                print(f"📅 Reporte del {reporte['date']}")
                print(f"   📊 Total asistencias: {reporte['total_attendance']}")
                print(f"   🧑‍🎓 Estudiantes únicos: {reporte['students_present']}")
                
                if reporte['by_classroom']:
                    print(f"   🏫 Por aula:")
                    for aula, cantidad in reporte['by_classroom'].items():
                        print(f"      - {aula}: {cantidad}")
                
                if reporte['by_hour']:
                    print(f"   ⏰ Por hora:")
                    for hora, cantidad in reporte['by_hour'].items():
                        print(f"      - {hora}:00: {cantidad}")
            else:
                print("❌ Error generando reporte")
                
        except Exception as e:
            print(f"❌ Error creando reporte: {e}")
    
    def ejemplo_sincronizacion(self):
        """Ejemplo de cómo sincronizar datos con Firebase"""
        print("\n🔄 Ejemplo: Sincronización con Firebase")
        print("-" * 40)
        
        if not FIREBASE_AVAILABLE:
            print("⚠️ Firebase no disponible para sincronización")
            return
        
        try:
            # Intentar sincronizar datos locales pendientes
            success = sync_to_firebase()
            
            if success:
                print("✅ Sincronización completada")
            else:
                print("⚠️ Sincronización no necesaria o falló")
                
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
    
    def ejemplo_estado_conexion(self):
        """Ejemplo de cómo verificar el estado de conexión"""
        print("\n🔗 Ejemplo: Estado de Conexión")
        print("-" * 40)
        
        if not FIREBASE_AVAILABLE:
            print("❌ Firebase Integration no disponible")
            return
        
        try:
            integration = get_integration()
            status = integration.get_connection_status()
            
            print(f"🔗 Firebase disponible: {status.get('firebase_available', False)}")
            print(f"🏠 Modo local: {status.get('local_mode', True)}")
            print(f"📦 Project ID: {status.get('project_id', 'N/A')}")
            print(f"🗄️ Firestore: {status.get('has_firestore', False)}")
            print(f"📁 Storage: {status.get('has_storage', False)}")
            print(f"💾 Dir. local: {status.get('local_data_dir', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error verificando estado: {e}")
    
    def _registro_local_estudiante(self, data):
        """Fallback para registro local de estudiante"""
        try:
            students_file = self.data_dir / "students.json"
            
            if students_file.exists():
                with open(students_file, 'r', encoding='utf-8') as f:
                    students = json.load(f)
            else:
                students = {}
            
            students[data['id']] = data
            
            with open(students_file, 'w', encoding='utf-8') as f:
                json.dump(students, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 Estudiante guardado localmente: {data['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando localmente: {e}")
            return False
    
    def _registro_local_asistencia(self, student_data, detection_info):
        """Fallback para registro local de asistencia"""
        try:
            attendance_file = self.data_dir / "attendance.json"
            
            if attendance_file.exists():
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance = json.load(f)
            else:
                attendance = []
            
            record = {
                'student_id': student_data['id'],
                'student_name': student_data['name'],
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'confidence': detection_info['confidence'],
                'method': detection_info['method']
            }
            
            attendance.append(record)
            
            with open(attendance_file, 'w', encoding='utf-8') as f:
                json.dump(attendance, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 Asistencia guardada localmente: {student_data['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando asistencia localmente: {e}")
            return False

def main():
    """Función principal de demostración"""
    print("🔥 Ejemplo de Integración Firebase con AsistoYA")
    print("=" * 50)
    
    # Crear instancia del ejemplo
    ejemplo = AsistoYAFirebaseExample()
    
    # Verificar estado de conexión
    ejemplo.ejemplo_estado_conexion()
    
    # Ejecutar ejemplos
    ejemplo.ejemplo_registro_estudiante()
    ejemplo.ejemplo_registro_asistencia()
    ejemplo.ejemplo_consulta_registros()
    ejemplo.ejemplo_reporte_diario()
    ejemplo.ejemplo_sincronizacion()
    
    print("\n" + "=" * 50)
    print("✅ Ejemplos de integración completados!")
    print("\n💡 Cómo usar en tu código AsistoYA:")
    print("   1. from firebase_integration import save_attendance, register_student")
    print("   2. Reemplaza llamadas de guardado local con las nuevas funciones")
    print("   3. El sistema maneja automáticamente Firebase vs modo local")
    print("   4. No necesitas cambiar la UI ni la lógica existente")

if __name__ == "__main__":
    main()
