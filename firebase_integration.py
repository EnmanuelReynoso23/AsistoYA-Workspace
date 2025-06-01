"""
🔥 Firebase Integration - AsistoYA
Integración del sistema AsistoYA con Firebase mejorado
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent))

try:
    from firebase.firebase_config_improved import get_firebase_manager, initialize_firebase
except ImportError as e:
    print(f"❌ Error importando Firebase: {e}")
    print("Continuando en modo local...")

class AsistoYAFirebaseIntegration:
    """Integración entre AsistoYA y Firebase"""
    
    def __init__(self):
        self.firebase_manager = None
        self.firebase_available = False
        self.local_data_dir = Path(__file__).parent / "data"
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializar Firebase si está disponible"""
        try:
            success = initialize_firebase()
            if success:
                self.firebase_manager = get_firebase_manager()
                self.firebase_available = True
                print("✅ Firebase integrado correctamente")
            else:
                print("⚠️ Firebase no disponible, usando modo local")
        except Exception as e:
            print(f"⚠️ Error inicializando Firebase: {e}")
            print("Continuando en modo local...")
    
    def save_attendance(self, student_data, detection_info=None):
        """
        Guardar registro de asistencia con integración Firebase
        
        Args:
            student_data: Información del estudiante (dict)
            detection_info: Información de detección facial (dict, opcional)
        """
        try:
            # Preparar registro de asistencia
            attendance_record = {
                'student_id': student_data.get('id', student_data.get('student_id', 'unknown')),
                'student_name': student_data.get('name', student_data.get('student_name', 'Unknown')),
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'status': 'present',
                'method': 'face_recognition',
                'classroom': student_data.get('classroom', 'default'),
                'grade': student_data.get('grade', student_data.get('curso', '')),
                'confidence': detection_info.get('confidence', 0.0) if detection_info else 0.0,
                'detection_method': detection_info.get('method', 'unknown') if detection_info else 'manual'
            }
            
            # Intentar guardar en Firebase
            if self.firebase_available and self.firebase_manager:
                success = self.firebase_manager.save_attendance_record(attendance_record)
                if success:
                    print(f"✅ Asistencia guardada en Firebase: {attendance_record['student_name']}")
                    return True
            
            # Fallback a guardado local
            return self._save_local_attendance(attendance_record)
            
        except Exception as e:
            print(f"❌ Error guardando asistencia: {e}")
            return self._save_local_attendance(attendance_record)
    
    def _save_local_attendance(self, record):
        """Guardar asistencia localmente como fallback"""
        try:
            # Usar el formato de archivo existente de AsistoYA
            attendance_file = self.local_data_dir / "attendance.json"
            
            # Leer registros existentes
            if attendance_file.exists():
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance_data = json.load(f)
            else:
                attendance_data = []
            
            # Agregar nuevo registro
            attendance_data.append(record)
            
            # Guardar archivo actualizado
            with open(attendance_file, 'w', encoding='utf-8') as f:
                json.dump(attendance_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 Asistencia guardada localmente: {record['student_name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando localmente: {e}")
            return False
    
    def register_student(self, student_data):
        """
        Registrar estudiante con integración Firebase
        
        Args:
            student_data: Información del estudiante (dict)
        """
        try:
            # Preparar datos del estudiante
            student_record = {
                'student_id': student_data.get('id', student_data.get('student_id')),
                'name': student_data.get('name', student_data.get('nombre')),
                'email': student_data.get('email', ''),
                'phone': student_data.get('phone', student_data.get('telefono', '')),
                'grade': student_data.get('grade', student_data.get('curso', '')),
                'classroom': student_data.get('classroom', student_data.get('aula', '')),
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'face_encoding_available': 'face_encoding' in student_data,
                'registration_method': 'face_recognition'
            }
            
            # Intentar guardar en Firebase
            if self.firebase_available and self.firebase_manager:
                success = self.firebase_manager.save_student_data(
                    student_record['student_id'], 
                    student_record
                )
                if success:
                    print(f"✅ Estudiante registrado en Firebase: {student_record['name']}")
                    return True
            
            # Fallback a guardado local
            return self._save_local_student(student_record)
            
        except Exception as e:
            print(f"❌ Error registrando estudiante: {e}")
            return self._save_local_student(student_record)
    
    def _save_local_student(self, record):
        """Guardar estudiante localmente como fallback"""
        try:
            # Usar el formato de archivo existente de AsistoYA
            students_file = self.local_data_dir / "students.json"
            
            # Leer estudiantes existentes
            if students_file.exists():
                with open(students_file, 'r', encoding='utf-8') as f:
                    students_data = json.load(f)
            else:
                students_data = {}
            
            # Agregar/actualizar estudiante
            students_data[record['student_id']] = record
            
            # Guardar archivo actualizado
            with open(students_file, 'w', encoding='utf-8') as f:
                json.dump(students_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 Estudiante guardado localmente: {record['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando estudiante localmente: {e}")
            return False
    
    def get_attendance_records(self, filters=None):
        """
        Obtener registros de asistencia con integración Firebase
        
        Args:
            filters: Filtros a aplicar (dict, opcional)
        
        Returns:
            list: Lista de registros de asistencia
        """
        try:
            # Intentar obtener de Firebase
            if self.firebase_available and self.firebase_manager:
                records = self.firebase_manager.get_attendance_records(filters)
                if records:
                    return records
            
            # Fallback a datos locales
            return self._get_local_attendance(filters)
            
        except Exception as e:
            print(f"❌ Error obteniendo registros: {e}")
            return self._get_local_attendance(filters)
    
    def _get_local_attendance(self, filters=None):
        """Obtener registros de asistencia locales"""
        try:
            attendance_file = self.local_data_dir / "attendance.json"
            
            if not attendance_file.exists():
                return []
            
            with open(attendance_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            # Aplicar filtros si se proporcionan
            if filters:
                filtered_records = []
                for record in records:
                    matches = True
                    for key, value in filters.items():
                        if record.get(key) != value:
                            matches = False
                            break
                    if matches:
                        filtered_records.append(record)
                return filtered_records
            
            return records
            
        except Exception as e:
            print(f"❌ Error leyendo registros locales: {e}")
            return []
    
    def sync_local_data_to_firebase(self):
        """Sincronizar datos locales existentes con Firebase"""
        if not self.firebase_available:
            print("⚠️ Firebase no disponible para sincronización")
            return False
        
        try:
            synced_count = 0
            
            # Sincronizar estudiantes
            students_file = self.local_data_dir / "students.json"
            if students_file.exists():
                with open(students_file, 'r', encoding='utf-8') as f:
                    students_data = json.load(f)
                
                for student_id, student_info in students_data.items():
                    success = self.firebase_manager.save_student_data(student_id, student_info)
                    if success:
                        synced_count += 1
                        print(f"🔄 Estudiante sincronizado: {student_info.get('name', student_id)}")
            
            # Sincronizar asistencia
            attendance_file = self.local_data_dir / "attendance.json"
            if attendance_file.exists():
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance_data = json.load(f)
                
                for record in attendance_data:
                    success = self.firebase_manager.save_attendance_record(record)
                    if success:
                        synced_count += 1
                        print(f"🔄 Asistencia sincronizada: {record.get('student_name', 'Unknown')}")
            
            print(f"✅ {synced_count} registros sincronizados con Firebase")
            return True
            
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
            return False
    
    def get_connection_status(self):
        """Obtener estado de conexión"""
        status = {
            'firebase_available': self.firebase_available,
            'local_mode': not self.firebase_available,
            'firebase_connected': False,
            'project_id': None
        }
        
        if self.firebase_manager:
            firebase_status = self.firebase_manager.get_connection_status()
            status.update(firebase_status)
        
        return status
    
    def create_daily_report(self, date=None):
        """Crear reporte diario de asistencia"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Obtener registros del día
            records = self.get_attendance_records({'date': date})
            
            # Generar estadísticas
            report = {
                'date': date,
                'total_attendance': len(records),
                'students_present': len(set(r['student_id'] for r in records)),
                'by_classroom': {},
                'by_hour': {},
                'records': records
            }
            
            # Agrupar por aula
            for record in records:
                classroom = record.get('classroom', 'default')
                if classroom not in report['by_classroom']:
                    report['by_classroom'][classroom] = 0
                report['by_classroom'][classroom] += 1
            
            # Agrupar por hora
            for record in records:
                hour = record.get('time', '00:00:00')[:2]
                if hour not in report['by_hour']:
                    report['by_hour'][hour] = 0
                report['by_hour'][hour] += 1
            
            return report
            
        except Exception as e:
            print(f"❌ Error creando reporte: {e}")
            return None

# Instancia global
_integration_instance = None

def get_integration():
    """Obtener instancia singleton de integración"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = AsistoYAFirebaseIntegration()
    return _integration_instance

# Funciones de conveniencia para compatibilidad
def save_attendance(student_data, detection_info=None):
    """Función de conveniencia para guardar asistencia"""
    integration = get_integration()
    return integration.save_attendance(student_data, detection_info)

def register_student(student_data):
    """Función de conveniencia para registrar estudiante"""
    integration = get_integration()
    return integration.register_student(student_data)

def get_attendance_records(filters=None):
    """Función de conveniencia para obtener registros"""
    integration = get_integration()
    return integration.get_attendance_records(filters)

def sync_to_firebase():
    """Función de conveniencia para sincronizar con Firebase"""
    integration = get_integration()
    return integration.sync_local_data_to_firebase()

if __name__ == "__main__":
    print("🔥 AsistoYA Firebase Integration Test")
    print("====================================")
    
    # Crear instancia de integración
    integration = get_integration()
    
    # Mostrar estado de conexión
    status = integration.get_connection_status()
    print(f"\n📊 Estado de Conexión:")
    print(f"   🔗 Firebase disponible: {status['firebase_available']}")
    print(f"   🏠 Modo local: {status['local_mode']}")
    if status.get('project_id'):
        print(f"   📦 Project ID: {status['project_id']}")
    
    # Prueba de registro de estudiante
    print(f"\n🧪 Prueba de registro...")
    test_student = {
        'id': 'TEST_INTEGRATION_001',
        'name': 'Estudiante Test Integración',
        'email': 'test.integration@asistoya.com',
        'grade': '11vo',
        'classroom': 'Aula Integración'
    }
    
    success = integration.register_student(test_student)
    print(f"   Registro: {'✅ Exitoso' if success else '❌ Falló'}")
    
    # Prueba de asistencia
    print(f"\n📝 Prueba de asistencia...")
    detection_info = {
        'confidence': 0.92,
        'method': 'face_recognition_test'
    }
    
    success = integration.save_attendance(test_student, detection_info)
    print(f"   Asistencia: {'✅ Exitoso' if success else '❌ Falló'}")
    
    # Obtener registros
    print(f"\n📋 Obteniendo registros...")
    records = integration.get_attendance_records()
    print(f"   {len(records)} registros encontrados")
    
    print(f"\n✅ Pruebas de integración completadas!")
