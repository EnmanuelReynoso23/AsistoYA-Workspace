#!/usr/bin/env python3
"""
AsistoYA - Gestor de Base de Datos
Manejo centralizado de almacenamiento en archivos JSON
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
import config

class DatabaseManager:
    """Gestor principal de base de datos JSON"""
    
    def __init__(self):
        """Inicializar el gestor de base de datos"""
        self.data_dir = config.DATA_DIR
        self.backup_dir = config.BACKUP_DIR
        
        # Asegurar que los directorios existen
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Inicializar archivos si no existen
        self._initialize_files()
    
    def _initialize_files(self):
        """Inicializar archivos de base de datos si no existen"""
        files_to_init = [
            (config.STUDENTS_FILE, []),
            (config.ATTENDANCE_FILE, []),
            (config.CLASSROOMS_FILE, [config.DEFAULT_CLASSROOM]),
            (config.USERS_FILE, [config.DEFAULT_ADMIN_USER]),
            (config.SETTINGS_FILE, config.DEFAULT_SETTINGS),
            (config.NAMES_DICT_FILE, {})
        ]
        
        for file_path, default_content in files_to_init:
            if not os.path.exists(file_path):
                self.save_json(file_path, default_content)
    
    def load_json(self, file_path: str) -> Any:
        """
        Cargar datos desde un archivo JSON
        
        Args:
            file_path: Ruta del archivo JSON
            
        Returns:
            Datos cargados del archivo
        """
        try:
            if not os.path.exists(file_path):
                return [] if file_path.endswith('.json') else {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return [] if file_path.endswith('.json') else {}
                return json.loads(content)
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}")
            return [] if file_path.endswith('.json') else {}
        except Exception as e:
            print(f"Unexpected error loading {file_path}: {e}")
            return [] if file_path.endswith('.json') else {}
    
    def save_json(self, file_path: str, data: Any) -> bool:
        """
        Guardar datos en un archivo JSON
        
        Args:
            file_path: Ruta del archivo JSON
            data: Datos a guardar
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Hacer backup antes de guardar
            if os.path.exists(file_path):
                self._backup_file(file_path)
            
            # Guardar datos
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False
    
    def _backup_file(self, file_path: str):
        """Crear backup de un archivo"""
        try:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{timestamp}_{filename}"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"Error creating backup for {file_path}: {e}")
    
    def get_all_records(self, table_name: str) -> List[Dict]:
        """
        Obtener todos los registros de una tabla
        
        Args:
            table_name: Nombre de la tabla (students, attendance, etc.)
            
        Returns:
            Lista de registros
        """
        file_path = self._get_file_path(table_name)
        return self.load_json(file_path)
    
    def add_record(self, table_name: str, record: Dict) -> bool:
        """
        Agregar un registro a una tabla
        
        Args:
            table_name: Nombre de la tabla
            record: Registro a agregar
            
        Returns:
            True si se agregó correctamente
        """
        try:
            file_path = self._get_file_path(table_name)
            records = self.load_json(file_path)
            
            # Agregar timestamp si no existe
            if 'created_at' not in record:
                record['created_at'] = datetime.now().isoformat()
            
            records.append(record)
            return self.save_json(file_path, records)
            
        except Exception as e:
            print(f"Error adding record to {table_name}: {e}")
            return False
    
    def update_record(self, table_name: str, record_id: str, 
                     updated_data: Dict, id_field: str = 'id') -> bool:
        """
        Actualizar un registro en una tabla
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro a actualizar
            updated_data: Datos actualizados
            id_field: Campo que actúa como ID
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            file_path = self._get_file_path(table_name)
            records = self.load_json(file_path)
            
            for record in records:
                if record.get(id_field) == record_id:
                    # Mantener timestamps originales
                    if 'created_at' in record and 'created_at' not in updated_data:
                        updated_data['created_at'] = record['created_at']
                    
                    # Agregar timestamp de actualización
                    updated_data['updated_at'] = datetime.now().isoformat()
                    
                    # Actualizar el registro
                    record.update(updated_data)
                    return self.save_json(file_path, records)
            
            return False  # Registro no encontrado
            
        except Exception as e:
            print(f"Error updating record in {table_name}: {e}")
            return False
    
    def delete_record(self, table_name: str, record_id: str, 
                     id_field: str = 'id') -> bool:
        """
        Eliminar un registro de una tabla
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro a eliminar
            id_field: Campo que actúa como ID
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            file_path = self._get_file_path(table_name)
            records = self.load_json(file_path)
            
            # Filtrar el registro a eliminar
            updated_records = [r for r in records if r.get(id_field) != record_id]
            
            if len(updated_records) < len(records):
                return self.save_json(file_path, updated_records)
            
            return False  # Registro no encontrado
            
        except Exception as e:
            print(f"Error deleting record from {table_name}: {e}")
            return False
    
    def find_record(self, table_name: str, **criteria) -> Optional[Dict]:
        """
        Buscar un registro por criterios
        
        Args:
            table_name: Nombre de la tabla
            **criteria: Criterios de búsqueda
            
        Returns:
            Primer registro que coincida o None
        """
        records = self.get_all_records(table_name)
        
        for record in records:
            match = True
            for key, value in criteria.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                return record
        
        return None
    
    def find_records(self, table_name: str, **criteria) -> List[Dict]:
        """
        Buscar múltiples registros por criterios
        
        Args:
            table_name: Nombre de la tabla
            **criteria: Criterios de búsqueda
            
        Returns:
            Lista de registros que coincidan
        """
        records = self.get_all_records(table_name)
        matching_records = []
        
        for record in records:
            match = True
            for key, value in criteria.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                matching_records.append(record)
        
        return matching_records
    
    def count_records(self, table_name: str, **criteria) -> int:
        """
        Contar registros que coincidan con criterios
        
        Args:
            table_name: Nombre de la tabla
            **criteria: Criterios de búsqueda
            
        Returns:
            Número de registros que coinciden
        """
        return len(self.find_records(table_name, **criteria))
    
    def _get_file_path(self, table_name: str) -> str:
        """Obtener la ruta del archivo para una tabla"""
        file_mapping = {
            'students': config.STUDENTS_FILE,
            'attendance': config.ATTENDANCE_FILE,
            'classrooms': config.CLASSROOMS_FILE,
            'users': config.USERS_FILE,
            'settings': config.SETTINGS_FILE,
            'names_dict': config.NAMES_DICT_FILE
        }
        
        return file_mapping.get(table_name, 
                               os.path.join(self.data_dir, f"{table_name}.json"))
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Obtener estadísticas generales de la base de datos
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {}
        
        tables = ['students', 'attendance', 'classrooms', 'users']
        
        for table in tables:
            try:
                records = self.get_all_records(table)
                stats[f'total_{table}'] = len(records)
                
                # Estadísticas adicionales para estudiantes
                if table == 'students':
                    active_students = len([r for r in records if r.get('active', True)])
                    stats['active_students'] = active_students
                
                # Estadísticas adicionales para asistencia
                elif table == 'attendance':
                    today = datetime.now().strftime(config.DATE_FORMAT)
                    today_attendance = len([r for r in records 
                                          if r.get('date') == today])
                    stats['today_attendance'] = today_attendance
                    
            except Exception as e:
                print(f"Error getting statistics for {table}: {e}")
                stats[f'total_{table}'] = 0
        
        return stats
    
    def backup_all_data(self) -> str:
        """
        Crear backup completo de todos los datos
        
        Returns:
            Ruta del archivo de backup creado
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"full_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Recopilar todos los datos
            all_data = {}
            
            tables = ['students', 'attendance', 'classrooms', 'users', 'settings']
            
            for table in tables:
                all_data[table] = self.get_all_records(table)
            
            # Guardar backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            return backup_path
            
        except Exception as e:
            print(f"Error creating full backup: {e}")
            return ""
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restaurar datos desde un backup
        
        Args:
            backup_path: Ruta del archivo de backup
            
        Returns:
            True si se restauró correctamente
        """
        try:
            if not os.path.exists(backup_path):
                print(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restaurar cada tabla
            for table_name, records in backup_data.items():
                file_path = self._get_file_path(table_name)
                if not self.save_json(file_path, records):
                    print(f"Error restoring table: {table_name}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """
        Limpiar backups antiguos
        
        Args:
            days_to_keep: Número de días de backups a mantener
        """
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        print(f"Removed old backup: {filename}")
                        
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")

# Crear instancia global del gestor de base de datos
db_manager = DatabaseManager()
