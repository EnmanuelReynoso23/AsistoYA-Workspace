#!/usr/bin/env python3
"""
AsistoYA - Modelo de Estudiantes
Gestión de datos y operaciones de estudiantes
"""

import os
import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from PIL import Image
import numpy as np

import config
from models.database import db_manager

class StudentModel:
    """Modelo para gestión de estudiantes"""
    
    def __init__(self):
        """Inicializar el modelo de estudiantes"""
        self.db = db_manager
        self.table_name = "students"
    
    def create_student(self, full_name: str, email: str = "", 
                      grade: str = "") -> Dict[str, Any]:
        """
        Crear un nuevo estudiante
        
        Args:
            full_name: Nombre completo del estudiante
            email: Email del estudiante (opcional)
            grade: Grado/curso del estudiante (opcional)
            
        Returns:
            Diccionario con el estudiante creado o información de error
        """
        try:
            # Validar datos de entrada
            validation_result = self._validate_student_data(full_name, email)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # Generar ID único
            student_id = self._generate_student_id(full_name)
            
            # Verificar que el ID sea único
            if self.get_student_by_id(student_id):
                student_id = self._generate_unique_student_id(full_name)
            
            # Crear el registro del estudiante
            student_data = {
                'student_id': student_id,
                'full_name': full_name.strip(),
                'email': email.strip().lower() if email else "",
                'grade': grade.strip() if grade else "",
                'active': True,
                'face_registered': False,
                'face_count': 0,
                'created_at': datetime.now().isoformat(),
                'last_attendance': None,
                'attendance_count': 0
            }
            
            # Guardar en la base de datos
            if self.db.add_record(self.table_name, student_data):
                return {
                    'success': True,
                    'message': 'Estudiante creado exitosamente',
                    'student': student_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al guardar el estudiante en la base de datos'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def get_all_students(self, active_only: bool = False) -> List[Dict]:
        """
        Obtener todos los estudiantes
        
        Args:
            active_only: Solo estudiantes activos
            
        Returns:
            Lista de estudiantes
        """
        try:
            students = self.db.get_all_records(self.table_name)
            
            if active_only:
                students = [s for s in students if s.get('active', True)]
            
            # Ordenar por nombre
            students.sort(key=lambda x: x.get('full_name', ''))
            
            return students
            
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """
        Obtener un estudiante por su ID
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Datos del estudiante o None si no existe
        """
        return self.db.find_record(self.table_name, student_id=student_id)
    
    def get_student_by_name(self, full_name: str) -> Optional[Dict]:
        """
        Obtener un estudiante por su nombre
        
        Args:
            full_name: Nombre completo del estudiante
            
        Returns:
            Datos del estudiante o None si no existe
        """
        return self.db.find_record(self.table_name, full_name=full_name.strip())
    
    def update_student(self, student_id: str, **updates) -> Dict[str, Any]:
        """
        Actualizar datos de un estudiante
        
        Args:
            student_id: ID del estudiante
            **updates: Campos a actualizar
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el estudiante existe
            student = self.get_student_by_id(student_id)
            if not student:
                return {
                    'success': False,
                    'message': 'Estudiante no encontrado'
                }
            
            # Validar datos si se están actualizando
            if 'full_name' in updates or 'email' in updates:
                full_name = updates.get('full_name', student['full_name'])
                email = updates.get('email', student['email'])
                
                validation_result = self._validate_student_data(full_name, email)
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'message': validation_result['message']
                    }
            
            # Actualizar en la base de datos
            if self.db.update_record(self.table_name, student_id, updates, 'student_id'):
                return {
                    'success': True,
                    'message': 'Estudiante actualizado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al actualizar el estudiante'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def delete_student(self, student_id: str, remove_faces: bool = True) -> Dict[str, Any]:
        """
        Eliminar un estudiante
        
        Args:
            student_id: ID del estudiante
            remove_faces: Si eliminar también los archivos de rostros
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el estudiante existe
            student = self.get_student_by_id(student_id)
            if not student:
                return {
                    'success': False,
                    'message': 'Estudiante no encontrado'
                }
            
            # Eliminar archivos de rostros si se solicita
            if remove_faces:
                self._remove_student_faces(student_id)
            
            # Eliminar de la base de datos
            if self.db.delete_record(self.table_name, student_id, 'student_id'):
                return {
                    'success': True,
                    'message': 'Estudiante eliminado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al eliminar el estudiante'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def register_face_images(self, student_id: str, face_images: List[np.ndarray]) -> Dict[str, Any]:
        """
        Registrar imágenes de rostros para un estudiante
        
        Args:
            student_id: ID del estudiante
            face_images: Lista de imágenes de rostros como arrays numpy
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el estudiante existe
            student = self.get_student_by_id(student_id)
            if not student:
                return {
                    'success': False,
                    'message': 'Estudiante no encontrado'
                }
            
            if not face_images:
                return {
                    'success': False,
                    'message': 'No se proporcionaron imágenes de rostros'
                }
            
            # Guardar las imágenes
            saved_files = []
            
            for i, face_image in enumerate(face_images):
                # Generar nombre de archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{student['full_name']}_{student_id}_{timestamp}_{i+1}.jpg"
                # Limpiar caracteres especiales del nombre
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                file_path = os.path.join(config.FACES_DIR, filename)
                
                try:
                    # Convertir numpy array a imagen PIL y guardar
                    if isinstance(face_image, np.ndarray):
                        # Asegurar que la imagen esté en formato correcto
                        if len(face_image.shape) == 3:
                            # Convertir BGR a RGB si es necesario
                            face_image = face_image[:, :, ::-1]
                        
                        image = Image.fromarray(face_image)
                        image.save(file_path, 'JPEG', quality=95)
                        saved_files.append(file_path)
                    
                except Exception as e:
                    print(f"Error saving face image {i+1}: {e}")
                    continue
            
            if saved_files:
                # Actualizar el registro del estudiante
                updates = {
                    'face_registered': True,
                    'face_count': len(saved_files),
                    'last_face_update': datetime.now().isoformat()
                }
                
                self.update_student(student_id, **updates)
                
                return {
                    'success': True,
                    'message': f'Se registraron {len(saved_files)} imágenes de rostros',
                    'files_saved': len(saved_files)
                }
            else:
                return {
                    'success': False,
                    'message': 'No se pudo guardar ninguna imagen de rostro'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error registrando rostros: {str(e)}'
            }
    
    def update_attendance_count(self, student_id: str) -> bool:
        """
        Actualizar el contador de asistencia de un estudiante
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            student = self.get_student_by_id(student_id)
            if not student:
                return False
            
            current_count = student.get('attendance_count', 0)
            updates = {
                'attendance_count': current_count + 1,
                'last_attendance': datetime.now().isoformat()
            }
            
            result = self.update_student(student_id, **updates)
            return result['success']
            
        except Exception as e:
            print(f"Error updating attendance count: {e}")
            return False
    
    def get_students_with_faces(self) -> List[Dict]:
        """
        Obtener estudiantes que tienen rostros registrados
        
        Returns:
            Lista de estudiantes con rostros registrados
        """
        students = self.get_all_students(active_only=True)
        return [s for s in students if s.get('face_registered', False)]
    
    def get_students_without_faces(self) -> List[Dict]:
        """
        Obtener estudiantes que no tienen rostros registrados
        
        Returns:
            Lista de estudiantes sin rostros registrados
        """
        students = self.get_all_students(active_only=True)
        return [s for s in students if not s.get('face_registered', False)]
    
    def search_students(self, query: str) -> List[Dict]:
        """
        Buscar estudiantes por nombre, email o ID
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de estudiantes que coinciden con la búsqueda
        """
        if not query:
            return self.get_all_students()
        
        query = query.lower().strip()
        all_students = self.get_all_students()
        
        matching_students = []
        
        for student in all_students:
            # Buscar en nombre
            if query in student.get('full_name', '').lower():
                matching_students.append(student)
                continue
            
            # Buscar en email
            if query in student.get('email', '').lower():
                matching_students.append(student)
                continue
            
            # Buscar en ID
            if query in student.get('student_id', '').lower():
                matching_students.append(student)
                continue
            
            # Buscar en grado
            if query in student.get('grade', '').lower():
                matching_students.append(student)
                continue
        
        return matching_students
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de estudiantes
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            all_students = self.get_all_students()
            active_students = [s for s in all_students if s.get('active', True)]
            students_with_faces = [s for s in active_students if s.get('face_registered', False)]
            
            # Calcular estadísticas de asistencia
            total_attendance = sum(s.get('attendance_count', 0) for s in active_students)
            avg_attendance = total_attendance / len(active_students) if active_students else 0
            
            return {
                'total_students': len(all_students),
                'active_students': len(active_students),
                'inactive_students': len(all_students) - len(active_students),
                'students_with_faces': len(students_with_faces),
                'students_without_faces': len(active_students) - len(students_with_faces),
                'total_attendance': total_attendance,
                'average_attendance': round(avg_attendance, 2),
                'face_registration_percentage': round(
                    (len(students_with_faces) / len(active_students) * 100) if active_students else 0, 2
                )
            }
            
        except Exception as e:
            print(f"Error getting student statistics: {e}")
            return {}
    
    def _validate_student_data(self, full_name: str, email: str = "") -> Dict[str, Any]:
        """
        Validar datos de estudiante
        
        Args:
            full_name: Nombre completo
            email: Email (opcional)
            
        Returns:
            Diccionario con resultado de validación
        """
        # Validar nombre
        if not full_name or not full_name.strip():
            return {
                'valid': False,
                'message': 'El nombre completo es obligatorio'
            }
        
        if len(full_name.strip()) < config.MIN_NAME_LENGTH:
            return {
                'valid': False,
                'message': f'El nombre debe tener al menos {config.MIN_NAME_LENGTH} caracteres'
            }
        
        if len(full_name.strip()) > config.MAX_NAME_LENGTH:
            return {
                'valid': False,
                'message': f'El nombre no puede exceder {config.MAX_NAME_LENGTH} caracteres'
            }
        
        # Validar email si se proporciona
        if email and email.strip():
            if len(email.strip()) < config.MIN_EMAIL_LENGTH:
                return {
                    'valid': False,
                    'message': f'El email debe tener al menos {config.MIN_EMAIL_LENGTH} caracteres'
                }
            
            if len(email.strip()) > config.MAX_EMAIL_LENGTH:
                return {
                    'valid': False,
                    'message': f'El email no puede exceder {config.MAX_EMAIL_LENGTH} caracteres'
                }
            
            if not re.match(config.EMAIL_PATTERN, email.strip()):
                return {
                    'valid': False,
                    'message': 'El email no tiene un formato válido'
                }
            
            # Verificar que el email sea único
            existing_student = self.db.find_record(self.table_name, email=email.strip().lower())
            if existing_student:
                return {
                    'valid': False,
                    'message': 'Ya existe un estudiante con este email'
                }
        
        # Verificar que el nombre sea único
        existing_student = self.db.find_record(self.table_name, full_name=full_name.strip())
        if existing_student:
            return {
                'valid': False,
                'message': 'Ya existe un estudiante con este nombre'
            }
        
        return {'valid': True, 'message': 'Datos válidos'}
    
    def _generate_student_id(self, full_name: str) -> str:
        """
        Generar ID único para estudiante
        
        Args:
            full_name: Nombre completo del estudiante
            
        Returns:
            ID generado
        """
        # Obtener iniciales del nombre
        words = full_name.strip().split()
        if len(words) >= 2:
            initials = words[0][:1] + words[-1][:1]
        else:
            initials = words[0][:2] if words else "XX"
        
        initials = initials.upper()
        
        # Generar número aleatorio
        import random
        number = random.randint(1000, 9999)
        
        return f"{initials}{number}"
    
    def _generate_unique_student_id(self, full_name: str) -> str:
        """
        Generar ID único garantizado
        
        Args:
            full_name: Nombre completo del estudiante
            
        Returns:
            ID único generado
        """
        base_id = self._generate_student_id(full_name)
        
        # Si ya existe, generar con UUID
        while self.get_student_by_id(base_id):
            suffix = str(uuid.uuid4())[:4].upper()
            base_id = f"{base_id[:2]}{suffix}"
        
        return base_id
    
    def _remove_student_faces(self, student_id: str):
        """
        Eliminar archivos de rostros de un estudiante
        
        Args:
            student_id: ID del estudiante
        """
        try:
            if not os.path.exists(config.FACES_DIR):
                return
            
            # Buscar archivos que contengan el student_id
            for filename in os.listdir(config.FACES_DIR):
                if student_id in filename:
                    file_path = os.path.join(config.FACES_DIR, filename)
                    try:
                        os.remove(file_path)
                        print(f"Removed face file: {filename}")
                    except Exception as e:
                        print(f"Error removing face file {filename}: {e}")
                        
        except Exception as e:
            print(f"Error removing student faces: {e}")

# Crear instancia global del modelo de estudiantes
student_model = StudentModel()
