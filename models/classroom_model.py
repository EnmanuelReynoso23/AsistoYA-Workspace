#!/usr/bin/env python3
"""
AsistoYA - Modelo de Aulas
Gestión de aulas y salones de clase
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

import config
from models.database import db_manager

class ClassroomModel:
    """Modelo para gestión de aulas"""
    
    def __init__(self):
        """Inicializar el modelo de aulas"""
        self.db = db_manager
        self.table_name = "classrooms"
    
    def create_classroom(self, name: str, description: str = "",
                        capacity: int = 30, location: str = "") -> Dict[str, Any]:
        """
        Crear una nueva aula
        
        Args:
            name: Nombre del aula
            description: Descripción del aula
            capacity: Capacidad del aula
            location: Ubicación del aula
            
        Returns:
            Resultado de la operación
        """
        try:
            # Validar datos
            validation_result = self._validate_classroom_data(name, capacity)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # Verificar que el nombre sea único
            if self.get_classroom_by_name(name):
                return {
                    'success': False,
                    'message': 'Ya existe un aula con este nombre'
                }
            
            # Generar ID único
            classroom_id = self._generate_classroom_id(name)
            
            # Crear registro del aula
            classroom_data = {
                'classroom_id': classroom_id,
                'name': name.strip(),
                'description': description.strip(),
                'capacity': capacity,
                'location': location.strip(),
                'active': True,
                'created_at': datetime.now().isoformat(),
                'student_count': 0,
                'total_sessions': 0
            }
            
            # Guardar en base de datos
            if self.db.add_record(self.table_name, classroom_data):
                return {
                    'success': True,
                    'message': 'Aula creada exitosamente',
                    'classroom': classroom_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al guardar el aula'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def get_all_classrooms(self, active_only: bool = False) -> List[Dict]:
        """
        Obtener todas las aulas
        
        Args:
            active_only: Solo aulas activas
            
        Returns:
            Lista de aulas
        """
        try:
            classrooms = self.db.get_all_records(self.table_name)
            
            if active_only:
                classrooms = [c for c in classrooms if c.get('active', True)]
            
            # Ordenar por nombre
            classrooms.sort(key=lambda x: x.get('name', ''))
            
            return classrooms
            
        except Exception as e:
            print(f"Error getting classrooms: {e}")
            return []
    
    def get_classroom_by_id(self, classroom_id: str) -> Optional[Dict]:
        """
        Obtener aula por ID
        
        Args:
            classroom_id: ID del aula
            
        Returns:
            Datos del aula o None
        """
        return self.db.find_record(self.table_name, classroom_id=classroom_id)
    
    def get_classroom_by_name(self, name: str) -> Optional[Dict]:
        """
        Obtener aula por nombre
        
        Args:
            name: Nombre del aula
            
        Returns:
            Datos del aula o None
        """
        return self.db.find_record(self.table_name, name=name.strip())
    
    def update_classroom(self, classroom_id: str, **updates) -> Dict[str, Any]:
        """
        Actualizar datos de un aula
        
        Args:
            classroom_id: ID del aula
            **updates: Campos a actualizar
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el aula existe
            classroom = self.get_classroom_by_id(classroom_id)
            if not classroom:
                return {
                    'success': False,
                    'message': 'Aula no encontrada'
                }
            
            # Validar datos si se están actualizando
            if 'name' in updates or 'capacity' in updates:
                name = updates.get('name', classroom['name'])
                capacity = updates.get('capacity', classroom['capacity'])
                
                validation_result = self._validate_classroom_data(name, capacity)
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'message': validation_result['message']
                    }
                
                # Verificar unicidad del nombre si se está cambiando
                if 'name' in updates and updates['name'] != classroom['name']:
                    if self.get_classroom_by_name(name):
                        return {
                            'success': False,
                            'message': 'Ya existe un aula con este nombre'
                        }
            
            # Actualizar en base de datos
            if self.db.update_record(self.table_name, classroom_id, updates, 'classroom_id'):
                return {
                    'success': True,
                    'message': 'Aula actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al actualizar el aula'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def delete_classroom(self, classroom_id: str) -> Dict[str, Any]:
        """
        Eliminar un aula
        
        Args:
            classroom_id: ID del aula
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el aula existe
            classroom = self.get_classroom_by_id(classroom_id)
            if not classroom:
                return {
                    'success': False,
                    'message': 'Aula no encontrada'
                }
            
            # Verificar si hay registros de asistencia asociados
            from models.student_model import student_model
            attendance_records = self.db.find_records('attendance', classroom_id=classroom_id)
            
            if attendance_records:
                return {
                    'success': False,
                    'message': 'No se puede eliminar el aula porque tiene registros de asistencia asociados'
                }
            
            # Eliminar de base de datos
            if self.db.delete_record(self.table_name, classroom_id, 'classroom_id'):
                return {
                    'success': True,
                    'message': 'Aula eliminada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al eliminar el aula'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def assign_students_to_classroom(self, classroom_id: str, 
                                   student_ids: List[str]) -> Dict[str, Any]:
        """
        Asignar estudiantes a un aula
        
        Args:
            classroom_id: ID del aula
            student_ids: Lista de IDs de estudiantes
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el aula existe
            classroom = self.get_classroom_by_id(classroom_id)
            if not classroom:
                return {
                    'success': False,
                    'message': 'Aula no encontrada'
                }
            
            # Verificar capacidad
            if len(student_ids) > classroom.get('capacity', 30):
                return {
                    'success': False,
                    'message': f'La capacidad del aula es de {classroom["capacity"]} estudiantes'
                }
            
            # Verificar que todos los estudiantes existen
            from models.student_model import student_model
            valid_students = []
            
            for student_id in student_ids:
                student = student_model.get_student_by_id(student_id)
                if student and student.get('active', True):
                    valid_students.append(student_id)
            
            if not valid_students:
                return {
                    'success': False,
                    'message': 'No se encontraron estudiantes válidos'
                }
            
            # Actualizar el contador de estudiantes en el aula
            updates = {
                'student_count': len(valid_students),
                'assigned_students': valid_students,
                'last_assignment': datetime.now().isoformat()
            }
            
            if self.update_classroom(classroom_id, **updates)['success']:
                return {
                    'success': True,
                    'message': f'Se asignaron {len(valid_students)} estudiantes al aula',
                    'assigned_count': len(valid_students)
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al asignar estudiantes al aula'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def get_classroom_students(self, classroom_id: str) -> List[Dict]:
        """
        Obtener estudiantes asignados a un aula
        
        Args:
            classroom_id: ID del aula
            
        Returns:
            Lista de estudiantes asignados
        """
        try:
            classroom = self.get_classroom_by_id(classroom_id)
            if not classroom:
                return []
            
            assigned_student_ids = classroom.get('assigned_students', [])
            if not assigned_student_ids:
                return []
            
            from models.student_model import student_model
            students = []
            
            for student_id in assigned_student_ids:
                student = student_model.get_student_by_id(student_id)
                if student:
                    students.append(student)
            
            return students
            
        except Exception as e:
            print(f"Error getting classroom students: {e}")
            return []
    
    def get_classroom_attendance_stats(self, classroom_id: str) -> Dict[str, Any]:
        """
        Obtener estadísticas de asistencia de un aula
        
        Args:
            classroom_id: ID del aula
            
        Returns:
            Estadísticas de asistencia
        """
        try:
            # Obtener registros de asistencia del aula
            attendance_records = self.db.find_records('attendance', classroom_id=classroom_id)
            
            # Calcular estadísticas
            total_records = len(attendance_records)
            unique_students = len(set(record.get('student_id', '') for record in attendance_records))
            
            # Asistencia por fecha
            dates = {}
            for record in attendance_records:
                date = record.get('date', '')
                if date:
                    dates[date] = dates.get(date, 0) + 1
            
            # Asistencia reciente (últimos 7 días)
            from datetime import datetime, timedelta
            recent_date = (datetime.now() - timedelta(days=7)).strftime(config.DATE_FORMAT)
            recent_records = [r for r in attendance_records if r.get('date', '') >= recent_date]
            
            return {
                'total_attendance_records': total_records,
                'unique_students_attended': unique_students,
                'attendance_by_date': dates,
                'recent_attendance': len(recent_records),
                'average_daily_attendance': round(total_records / max(len(dates), 1), 2),
                'most_active_date': max(dates.items(), key=lambda x: x[1]) if dates else None
            }
            
        except Exception as e:
            print(f"Error getting classroom attendance stats: {e}")
            return {}
    
    def search_classrooms(self, query: str) -> List[Dict]:
        """
        Buscar aulas por nombre, descripción o ubicación
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de aulas que coinciden
        """
        if not query:
            return self.get_all_classrooms()
        
        query = query.lower().strip()
        all_classrooms = self.get_all_classrooms()
        
        matching_classrooms = []
        
        for classroom in all_classrooms:
            # Buscar en nombre
            if query in classroom.get('name', '').lower():
                matching_classrooms.append(classroom)
                continue
            
            # Buscar en descripción
            if query in classroom.get('description', '').lower():
                matching_classrooms.append(classroom)
                continue
            
            # Buscar en ubicación
            if query in classroom.get('location', '').lower():
                matching_classrooms.append(classroom)
                continue
            
            # Buscar en ID
            if query in classroom.get('classroom_id', '').lower():
                matching_classrooms.append(classroom)
                continue
        
        return matching_classrooms
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de aulas
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            all_classrooms = self.get_all_classrooms()
            active_classrooms = [c for c in all_classrooms if c.get('active', True)]
            
            # Calcular capacidades
            total_capacity = sum(c.get('capacity', 0) for c in active_classrooms)
            total_students = sum(c.get('student_count', 0) for c in active_classrooms)
            avg_capacity = total_capacity / len(active_classrooms) if active_classrooms else 0
            
            # Utilización
            utilization_rate = (total_students / total_capacity * 100) if total_capacity > 0 else 0
            
            # Aulas por ubicación
            locations = {}
            for classroom in active_classrooms:
                location = classroom.get('location', 'Sin ubicación')
                locations[location] = locations.get(location, 0) + 1
            
            return {
                'total_classrooms': len(all_classrooms),
                'active_classrooms': len(active_classrooms),
                'inactive_classrooms': len(all_classrooms) - len(active_classrooms),
                'total_capacity': total_capacity,
                'total_assigned_students': total_students,
                'average_capacity': round(avg_capacity, 2),
                'utilization_rate': round(utilization_rate, 2),
                'locations_distribution': locations,
                'empty_classrooms': len([c for c in active_classrooms if c.get('student_count', 0) == 0]),
                'full_classrooms': len([c for c in active_classrooms 
                                      if c.get('student_count', 0) >= c.get('capacity', 0)])
            }
            
        except Exception as e:
            print(f"Error getting classroom statistics: {e}")
            return {}
    
    def increment_session_count(self, classroom_id: str) -> bool:
        """
        Incrementar el contador de sesiones de un aula
        
        Args:
            classroom_id: ID del aula
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            classroom = self.get_classroom_by_id(classroom_id)
            if not classroom:
                return False
            
            current_sessions = classroom.get('total_sessions', 0)
            updates = {
                'total_sessions': current_sessions + 1,
                'last_session': datetime.now().isoformat()
            }
            
            result = self.update_classroom(classroom_id, **updates)
            return result['success']
            
        except Exception as e:
            print(f"Error incrementing session count: {e}")
            return False
    
    def get_available_classrooms(self, required_capacity: int = 1) -> List[Dict]:
        """
        Obtener aulas disponibles con capacidad suficiente
        
        Args:
            required_capacity: Capacidad mínima requerida
            
        Returns:
            Lista de aulas disponibles
        """
        active_classrooms = self.get_all_classrooms(active_only=True)
        
        available_classrooms = []
        for classroom in active_classrooms:
            capacity = classroom.get('capacity', 0)
            current_students = classroom.get('student_count', 0)
            available_space = capacity - current_students
            
            if available_space >= required_capacity:
                classroom_info = classroom.copy()
                classroom_info['available_space'] = available_space
                available_classrooms.append(classroom_info)
        
        # Ordenar por espacio disponible (descendente)
        available_classrooms.sort(key=lambda x: x['available_space'], reverse=True)
        
        return available_classrooms
    
    def _validate_classroom_data(self, name: str, capacity: int) -> Dict[str, Any]:
        """
        Validar datos de aula
        
        Args:
            name: Nombre del aula
            capacity: Capacidad del aula
            
        Returns:
            Resultado de validación
        """
        # Validar nombre
        if not name or not name.strip():
            return {
                'valid': False,
                'message': 'El nombre del aula es obligatorio'
            }
        
        if len(name.strip()) < 2:
            return {
                'valid': False,
                'message': 'El nombre del aula debe tener al menos 2 caracteres'
            }
        
        if len(name.strip()) > 100:
            return {
                'valid': False,
                'message': 'El nombre del aula no puede exceder 100 caracteres'
            }
        
        # Validar capacidad
        if not isinstance(capacity, int) or capacity < 1:
            return {
                'valid': False,
                'message': 'La capacidad debe ser un número entero mayor a 0'
            }
        
        if capacity > 200:
            return {
                'valid': False,
                'message': 'La capacidad no puede exceder 200 estudiantes'
            }
        
        return {'valid': True, 'message': 'Datos válidos'}
    
    def _generate_classroom_id(self, name: str) -> str:
        """
        Generar ID único para aula
        
        Args:
            name: Nombre del aula
            
        Returns:
            ID generado
        """
        # Crear ID basado en el nombre
        clean_name = ''.join(c.upper() for c in name if c.isalnum())[:4]
        if len(clean_name) < 2:
            clean_name = "AULA"
        
        # Agregar sufijo único
        suffix = str(uuid.uuid4())[:4].upper()
        
        return f"AULA_{clean_name}_{suffix}"

# Crear instancia global del modelo de aulas
classroom_model = ClassroomModel()
