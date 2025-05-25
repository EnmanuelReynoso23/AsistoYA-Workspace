#!/usr/bin/env python3
"""
AsistoYA - Modelo de Asistencia
Gestión de registros de asistencia
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

import config
from models.database import db_manager

class AttendanceModel:
    """Modelo para gestión de asistencia"""
    
    def __init__(self):
        """Inicializar el modelo de asistencia"""
        self.db = db_manager
        self.table_name = "attendance"
        self.cooldown_cache = {}  # Cache para controlar cooldown
    
    def record_attendance(self, student_id: str, classroom_id: str = None,
                         confidence: float = 0.0, method: str = "facial_recognition") -> Dict[str, Any]:
        """
        Registrar asistencia de un estudiante
        
        Args:
            student_id: ID del estudiante
            classroom_id: ID del aula (opcional)
            confidence: Nivel de confianza del reconocimiento
            method: Método de registro (facial_recognition, manual, etc.)
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el estudiante existe
            from models.student_model import student_model
            student = student_model.get_student_by_id(student_id)
            if not student:
                return {
                    'success': False,
                    'message': 'Estudiante no encontrado'
                }
            
            if not student.get('active', True):
                return {
                    'success': False,
                    'message': 'Estudiante inactivo'
                }
            
            # Verificar cooldown
            cooldown_check = self._check_cooldown(student_id)
            if not cooldown_check['allowed']:
                return {
                    'success': False,
                    'message': cooldown_check['message']
                }
            
            # Obtener fecha y hora actual
            now = datetime.now()
            current_date = now.strftime(config.DATE_FORMAT)
            current_time = now.strftime(config.TIME_FORMAT)
            
            # Verificar si ya existe registro para hoy
            existing_record = self._get_today_attendance(student_id, current_date)
            if existing_record:
                return {
                    'success': False,
                    'message': f'Ya existe un registro de asistencia para {student["full_name"]} hoy',
                    'existing_record': existing_record
                }
            
            # Verificar aula si se proporciona
            if classroom_id:
                from models.classroom_model import classroom_model
                classroom = classroom_model.get_classroom_by_id(classroom_id)
                if not classroom:
                    classroom_id = None  # Usar aula por defecto
            
            # Generar ID único para el registro
            attendance_id = self._generate_attendance_id()
            
            # Crear registro de asistencia
            attendance_data = {
                'attendance_id': attendance_id,
                'student_id': student_id,
                'student_name': student['full_name'],
                'classroom_id': classroom_id or config.DEFAULT_CLASSROOM['classroom_id'],
                'date': current_date,
                'time': current_time,
                'timestamp': now.isoformat(),
                'confidence': confidence,
                'method': method,
                'status': 'present',
                'created_at': now.isoformat()
            }
            
            # Guardar en base de datos
            if self.db.add_record(self.table_name, attendance_data):
                # Actualizar contador de asistencia del estudiante
                student_model.update_attendance_count(student_id)
                
                # Actualizar cooldown
                self._update_cooldown(student_id, now)
                
                # Incrementar contador de sesiones del aula
                if classroom_id:
                    from models.classroom_model import classroom_model
                    classroom_model.increment_session_count(classroom_id)
                
                return {
                    'success': True,
                    'message': f'Asistencia registrada para {student["full_name"]}',
                    'attendance': attendance_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al guardar el registro de asistencia'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def get_all_attendance(self, date_filter: str = None) -> List[Dict]:
        """
        Obtener todos los registros de asistencia
        
        Args:
            date_filter: Fecha específica para filtrar (YYYY-MM-DD)
            
        Returns:
            Lista de registros de asistencia
        """
        try:
            if date_filter:
                records = self.db.find_records(self.table_name, date=date_filter)
            else:
                records = self.db.get_all_records(self.table_name)
            
            # Ordenar por fecha y hora (más recientes primero)
            records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return records
            
        except Exception as e:
            print(f"Error getting attendance records: {e}")
            return []
    
    def get_student_attendance(self, student_id: str, 
                             date_from: str = None, date_to: str = None) -> List[Dict]:
        """
        Obtener registros de asistencia de un estudiante
        
        Args:
            student_id: ID del estudiante
            date_from: Fecha inicial (YYYY-MM-DD)
            date_to: Fecha final (YYYY-MM-DD)
            
        Returns:
            Lista de registros del estudiante
        """
        try:
            records = self.db.find_records(self.table_name, student_id=student_id)
            
            # Filtrar por rango de fechas si se especifica
            if date_from or date_to:
                filtered_records = []
                for record in records:
                    record_date = record.get('date', '')
                    
                    if date_from and record_date < date_from:
                        continue
                    if date_to and record_date > date_to:
                        continue
                    
                    filtered_records.append(record)
                
                records = filtered_records
            
            # Ordenar por fecha
            records.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            return records
            
        except Exception as e:
            print(f"Error getting student attendance: {e}")
            return []
    
    def get_classroom_attendance(self, classroom_id: str, 
                               date_filter: str = None) -> List[Dict]:
        """
        Obtener registros de asistencia de un aula
        
        Args:
            classroom_id: ID del aula
            date_filter: Fecha específica (YYYY-MM-DD)
            
        Returns:
            Lista de registros del aula
        """
        try:
            if date_filter:
                records = self.db.find_records(self.table_name, 
                                             classroom_id=classroom_id, 
                                             date=date_filter)
            else:
                records = self.db.find_records(self.table_name, 
                                             classroom_id=classroom_id)
            
            # Ordenar por tiempo
            records.sort(key=lambda x: x.get('time', ''))
            
            return records
            
        except Exception as e:
            print(f"Error getting classroom attendance: {e}")
            return []
    
    def get_today_attendance(self) -> List[Dict]:
        """
        Obtener registros de asistencia de hoy
        
        Returns:
            Lista de registros de hoy
        """
        today = datetime.now().strftime(config.DATE_FORMAT)
        return self.get_all_attendance(date_filter=today)
    
    def update_attendance_record(self, attendance_id: str, **updates) -> Dict[str, Any]:
        """
        Actualizar un registro de asistencia
        
        Args:
            attendance_id: ID del registro
            **updates: Campos a actualizar
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el registro existe
            record = self.get_attendance_by_id(attendance_id)
            if not record:
                return {
                    'success': False,
                    'message': 'Registro de asistencia no encontrado'
                }
            
            # Actualizar en base de datos
            if self.db.update_record(self.table_name, attendance_id, updates, 'attendance_id'):
                return {
                    'success': True,
                    'message': 'Registro actualizado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al actualizar el registro'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def delete_attendance_record(self, attendance_id: str) -> Dict[str, Any]:
        """
        Eliminar un registro de asistencia
        
        Args:
            attendance_id: ID del registro
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el registro existe
            record = self.get_attendance_by_id(attendance_id)
            if not record:
                return {
                    'success': False,
                    'message': 'Registro de asistencia no encontrado'
                }
            
            # Eliminar de base de datos
            if self.db.delete_record(self.table_name, attendance_id, 'attendance_id'):
                return {
                    'success': True,
                    'message': 'Registro eliminado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al eliminar el registro'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def get_attendance_by_id(self, attendance_id: str) -> Optional[Dict]:
        """
        Obtener registro de asistencia por ID
        
        Args:
            attendance_id: ID del registro
            
        Returns:
            Datos del registro o None
        """
        return self.db.find_record(self.table_name, attendance_id=attendance_id)
    
    def get_attendance_statistics(self, date_from: str = None, 
                                date_to: str = None) -> Dict[str, Any]:
        """
        Obtener estadísticas de asistencia
        
        Args:
            date_from: Fecha inicial (YYYY-MM-DD)
            date_to: Fecha final (YYYY-MM-DD)
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Obtener todos los registros
            all_records = self.get_all_attendance()
            
            # Filtrar por rango de fechas si se especifica
            if date_from or date_to:
                filtered_records = []
                for record in all_records:
                    record_date = record.get('date', '')
                    
                    if date_from and record_date < date_from:
                        continue
                    if date_to and record_date > date_to:
                        continue
                    
                    filtered_records.append(record)
                
                all_records = filtered_records
            
            # Calcular estadísticas básicas
            total_records = len(all_records)
            unique_students = len(set(record.get('student_id', '') for record in all_records))
            unique_dates = len(set(record.get('date', '') for record in all_records))
            
            # Estadísticas por fecha
            daily_stats = {}
            for record in all_records:
                date = record.get('date', '')
                if date:
                    if date not in daily_stats:
                        daily_stats[date] = 0
                    daily_stats[date] += 1
            
            # Estadísticas por aula
            classroom_stats = {}
            for record in all_records:
                classroom_id = record.get('classroom_id', '')
                if classroom_id:
                    if classroom_id not in classroom_stats:
                        classroom_stats[classroom_id] = 0
                    classroom_stats[classroom_id] += 1
            
            # Estadísticas por método
            method_stats = {}
            for record in all_records:
                method = record.get('method', 'unknown')
                method_stats[method] = method_stats.get(method, 0) + 1
            
            # Promedio de confianza para reconocimiento facial
            facial_records = [r for r in all_records if r.get('method') == 'facial_recognition']
            avg_confidence = 0
            if facial_records:
                total_confidence = sum(r.get('confidence', 0) for r in facial_records)
                avg_confidence = total_confidence / len(facial_records)
            
            # Asistencia de hoy
            today = datetime.now().strftime(config.DATE_FORMAT)
            today_records = [r for r in all_records if r.get('date') == today]
            
            # Tendencia (últimos 7 días)
            week_ago = (datetime.now() - timedelta(days=7)).strftime(config.DATE_FORMAT)
            recent_records = [r for r in all_records if r.get('date', '') >= week_ago]
            
            return {
                'total_records': total_records,
                'unique_students': unique_students,
                'unique_dates': unique_dates,
                'average_daily_attendance': round(total_records / max(unique_dates, 1), 2),
                'daily_statistics': daily_stats,
                'classroom_statistics': classroom_stats,
                'method_statistics': method_stats,
                'average_confidence': round(avg_confidence, 2),
                'today_attendance': len(today_records),
                'recent_attendance': len(recent_records),
                'most_active_day': max(daily_stats.items(), key=lambda x: x[1]) if daily_stats else None,
                'most_active_classroom': max(classroom_stats.items(), key=lambda x: x[1]) if classroom_stats else None
            }
            
        except Exception as e:
            print(f"Error getting attendance statistics: {e}")
            return {}
    
    def get_student_attendance_summary(self, student_id: str, 
                                     days: int = 30) -> Dict[str, Any]:
        """
        Obtener resumen de asistencia de un estudiante
        
        Args:
            student_id: ID del estudiante
            days: Número de días atrás a considerar
            
        Returns:
            Resumen de asistencia del estudiante
        """
        try:
            # Calcular rango de fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            date_from = start_date.strftime(config.DATE_FORMAT)
            date_to = end_date.strftime(config.DATE_FORMAT)
            
            # Obtener registros del estudiante
            records = self.get_student_attendance(student_id, date_from, date_to)
            
            # Calcular estadísticas
            total_days = days
            attendance_days = len(records)
            attendance_rate = (attendance_days / total_days) * 100 if total_days > 0 else 0
            
            # Última asistencia
            last_attendance = records[0] if records else None
            
            # Racha actual (días consecutivos)
            current_streak = self._calculate_attendance_streak(student_id)
            
            # Asistencia por método
            methods = {}
            for record in records:
                method = record.get('method', 'unknown')
                methods[method] = methods.get(method, 0) + 1
            
            return {
                'student_id': student_id,
                'period_days': total_days,
                'attendance_days': attendance_days,
                'attendance_rate': round(attendance_rate, 2),
                'last_attendance': last_attendance,
                'current_streak': current_streak,
                'methods_used': methods,
                'records': records
            }
            
        except Exception as e:
            print(f"Error getting student attendance summary: {e}")
            return {}
    
    def generate_attendance_report(self, date_from: str, date_to: str,
                                 format_type: str = "summary") -> Dict[str, Any]:
        """
        Generar reporte de asistencia
        
        Args:
            date_from: Fecha inicial
            date_to: Fecha final
            format_type: Tipo de reporte (summary, detailed, csv)
            
        Returns:
            Datos del reporte
        """
        try:
            # Obtener registros del período
            all_records = self.get_all_attendance()
            
            # Filtrar por rango de fechas
            filtered_records = []
            for record in all_records:
                record_date = record.get('date', '')
                if date_from <= record_date <= date_to:
                    filtered_records.append(record)
            
            # Obtener información adicional
            from models.student_model import student_model
            from models.classroom_model import classroom_model
            
            students = {s['student_id']: s for s in student_model.get_all_students()}
            classrooms = {c['classroom_id']: c for c in classroom_model.get_all_classrooms()}
            
            # Enriquecer registros con información adicional
            enriched_records = []
            for record in filtered_records:
                enriched_record = record.copy()
                
                # Añadir información del estudiante
                student_id = record.get('student_id', '')
                if student_id in students:
                    student = students[student_id]
                    enriched_record['student_info'] = {
                        'full_name': student.get('full_name', ''),
                        'email': student.get('email', ''),
                        'grade': student.get('grade', '')
                    }
                
                # Añadir información del aula
                classroom_id = record.get('classroom_id', '')
                if classroom_id in classrooms:
                    classroom = classrooms[classroom_id]
                    enriched_record['classroom_info'] = {
                        'name': classroom.get('name', ''),
                        'location': classroom.get('location', '')
                    }
                
                enriched_records.append(enriched_record)
            
            # Generar estadísticas del reporte
            report_stats = self.get_attendance_statistics(date_from, date_to)
            
            return {
                'success': True,
                'report_type': format_type,
                'period': {
                    'from': date_from,
                    'to': date_to
                },
                'statistics': report_stats,
                'records': enriched_records,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}'
            }
    
    def _check_cooldown(self, student_id: str) -> Dict[str, Any]:
        """
        Verificar si un estudiante está en período de cooldown
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Resultado de la verificación
        """
        try:
            # Obtener configuración de cooldown
            cooldown_seconds = config.DEFAULT_ATTENDANCE_COOLDOWN
            
            # Verificar cache local
            if student_id in self.cooldown_cache:
                last_time = self.cooldown_cache[student_id]
                time_diff = (datetime.now() - last_time).total_seconds()
                
                if time_diff < cooldown_seconds:
                    remaining = int(cooldown_seconds - time_diff)
                    return {
                        'allowed': False,
                        'message': f'Debe esperar {remaining} segundos antes del próximo registro'
                    }
            
            # Verificar último registro en base de datos
            today = datetime.now().strftime(config.DATE_FORMAT)
            recent_records = self.db.find_records(self.table_name, 
                                                student_id=student_id, 
                                                date=today)
            
            if recent_records:
                # Ordenar por timestamp y obtener el más reciente
                recent_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                last_record = recent_records[0]
                
                try:
                    last_timestamp = datetime.fromisoformat(last_record['timestamp'])
                    time_diff = (datetime.now() - last_timestamp).total_seconds()
                    
                    if time_diff < cooldown_seconds:
                        remaining = int(cooldown_seconds - time_diff)
                        return {
                            'allowed': False,
                            'message': f'Debe esperar {remaining} segundos antes del próximo registro'
                        }
                except (ValueError, KeyError):
                    pass  # Si hay error en el timestamp, permitir el registro
            
            return {
                'allowed': True,
                'message': 'Registro permitido'
            }
            
        except Exception as e:
            print(f"Error checking cooldown: {e}")
            return {
                'allowed': True,
                'message': 'Registro permitido (error en verificación)'
            }
    
    def _update_cooldown(self, student_id: str, timestamp: datetime):
        """
        Actualizar el cache de cooldown
        
        Args:
            student_id: ID del estudiante
            timestamp: Timestamp del registro
        """
        self.cooldown_cache[student_id] = timestamp
    
    def _get_today_attendance(self, student_id: str, date: str) -> Optional[Dict]:
        """
        Verificar si ya existe registro de asistencia para hoy
        
        Args:
            student_id: ID del estudiante
            date: Fecha en formato YYYY-MM-DD
            
        Returns:
            Registro existente o None
        """
        records = self.db.find_records(self.table_name, 
                                     student_id=student_id, 
                                     date=date)
        return records[0] if records else None
    
    def _calculate_attendance_streak(self, student_id: str) -> int:
        """
        Calcular racha de asistencia consecutiva
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Número de días consecutivos de asistencia
        """
        try:
            # Obtener registros recientes del estudiante
            records = self.get_student_attendance(student_id)
            if not records:
                return 0
            
            # Ordenar por fecha (más reciente primero)
            records.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Calcular días consecutivos
            streak = 0
            current_date = datetime.now().date()
            
            for record in records:
                try:
                    record_date = datetime.strptime(record['date'], config.DATE_FORMAT).date()
                    
                    # Si es el primer registro y es de hoy, comenzar streak
                    if streak == 0 and record_date == current_date:
                        streak = 1
                        current_date -= timedelta(days=1)
                    # Si es el día anterior esperado, continuar streak
                    elif record_date == current_date:
                        streak += 1
                        current_date -= timedelta(days=1)
                    # Si hay un gap, terminar streak
                    else:
                        break
                        
                except (ValueError, KeyError):
                    continue
            
            return streak
            
        except Exception as e:
            print(f"Error calculating attendance streak: {e}")
            return 0
    
    def _generate_attendance_id(self) -> str:
        """
        Generar ID único para registro de asistencia
        
        Returns:
            ID único generado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = str(uuid.uuid4())[:8].upper()
        return f"ATT_{timestamp}_{unique_suffix}"

# Crear instancia global del modelo de asistencia
attendance_model = AttendanceModel()
