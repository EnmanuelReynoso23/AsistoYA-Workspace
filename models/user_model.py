#!/usr/bin/env python3
"""
AsistoYA - Modelo de Usuarios
Gestión de usuarios del sistema
"""

import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

import config
from models.database import db_manager

class UserModel:
    """Modelo para gestión de usuarios del sistema"""
    
    def __init__(self):
        """Inicializar el modelo de usuarios"""
        self.db = db_manager
        self.table_name = "users"
    
    def create_user(self, username: str, full_name: str, email: str,
                   password: str, role: str = "user") -> Dict[str, Any]:
        """
        Crear un nuevo usuario
        
        Args:
            username: Nombre de usuario único
            full_name: Nombre completo
            email: Email del usuario
            password: Contraseña
            role: Rol del usuario (admin, user, teacher)
            
        Returns:
            Resultado de la operación
        """
        try:
            # Validar datos
            validation_result = self._validate_user_data(username, full_name, email, password)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # Verificar que el username sea único
            if self.get_user_by_username(username):
                return {
                    'success': False,
                    'message': 'Ya existe un usuario con este nombre de usuario'
                }
            
            # Verificar que el email sea único
            if self.get_user_by_email(email):
                return {
                    'success': False,
                    'message': 'Ya existe un usuario con este email'
                }
            
            # Generar ID y hash de contraseña
            user_id = self._generate_user_id()
            password_hash = self._hash_password(password)
            
            # Crear registro de usuario
            user_data = {
                'user_id': user_id,
                'username': username.strip().lower(),
                'full_name': full_name.strip(),
                'email': email.strip().lower(),
                'password_hash': password_hash,
                'role': role.lower(),
                'active': True,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'login_count': 0
            }
            
            # Guardar en base de datos
            if self.db.add_record(self.table_name, user_data):
                # No devolver el hash de contraseña
                user_data_safe = user_data.copy()
                del user_data_safe['password_hash']
                
                return {
                    'success': True,
                    'message': 'Usuario creado exitosamente',
                    'user': user_data_safe
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al guardar el usuario'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autenticar un usuario
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña
            
        Returns:
            Resultado de la autenticación
        """
        try:
            # Buscar usuario por username o email
            user = self.get_user_by_username(username)
            if not user:
                user = self.get_user_by_email(username)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Usuario no encontrado'
                }
            
            # Verificar si el usuario está activo
            if not user.get('active', False):
                return {
                    'success': False,
                    'message': 'Usuario desactivado'
                }
            
            # Verificar contraseña
            if not self._verify_password(password, user['password_hash']):
                return {
                    'success': False,
                    'message': 'Contraseña incorrecta'
                }
            
            # Actualizar información de login
            self._update_login_info(user['user_id'])
            
            # Devolver información del usuario (sin contraseña)
            user_safe = user.copy()
            del user_safe['password_hash']
            
            return {
                'success': True,
                'message': 'Autenticación exitosa',
                'user': user_safe
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error en autenticación: {str(e)}'
            }
    
    def get_all_users(self, active_only: bool = False) -> List[Dict]:
        """
        Obtener todos los usuarios
        
        Args:
            active_only: Solo usuarios activos
            
        Returns:
            Lista de usuarios (sin contraseñas)
        """
        try:
            users = self.db.get_all_records(self.table_name)
            
            if active_only:
                users = [u for u in users if u.get('active', True)]
            
            # Remover contraseñas y ordenar por nombre
            users_safe = []
            for user in users:
                user_safe = user.copy()
                if 'password_hash' in user_safe:
                    del user_safe['password_hash']
                users_safe.append(user_safe)
            
            users_safe.sort(key=lambda x: x.get('full_name', ''))
            return users_safe
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Obtener usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Datos del usuario o None
        """
        return self.db.find_record(self.table_name, user_id=user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Obtener usuario por nombre de usuario
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Datos del usuario o None
        """
        return self.db.find_record(self.table_name, username=username.strip().lower())
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Obtener usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Datos del usuario o None
        """
        return self.db.find_record(self.table_name, email=email.strip().lower())
    
    def update_user(self, user_id: str, **updates) -> Dict[str, Any]:
        """
        Actualizar datos de usuario
        
        Args:
            user_id: ID del usuario
            **updates: Campos a actualizar
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el usuario existe
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'Usuario no encontrado'
                }
            
            # Si se está actualizando la contraseña, hashearla
            if 'password' in updates:
                updates['password_hash'] = self._hash_password(updates['password'])
                del updates['password']
            
            # Validar datos críticos si se están actualizando
            if any(key in updates for key in ['username', 'email', 'full_name']):
                username = updates.get('username', user['username'])
                email = updates.get('email', user['email'])
                full_name = updates.get('full_name', user['full_name'])
                
                # Verificar unicidad si se cambia username o email
                if 'username' in updates and updates['username'] != user['username']:
                    if self.get_user_by_username(username):
                        return {
                            'success': False,
                            'message': 'Ya existe un usuario con este nombre de usuario'
                        }
                
                if 'email' in updates and updates['email'] != user['email']:
                    if self.get_user_by_email(email):
                        return {
                            'success': False,
                            'message': 'Ya existe un usuario con este email'
                        }
            
            # Actualizar en base de datos
            if self.db.update_record(self.table_name, user_id, updates, 'user_id'):
                return {
                    'success': True,
                    'message': 'Usuario actualizado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al actualizar el usuario'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Eliminar un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar que el usuario existe
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'Usuario no encontrado'
                }
            
            # No permitir eliminar el último administrador
            if user.get('role') == 'admin':
                admin_count = len([u for u in self.get_all_users(active_only=True) 
                                 if u.get('role') == 'admin'])
                if admin_count <= 1:
                    return {
                        'success': False,
                        'message': 'No se puede eliminar el último administrador'
                    }
            
            # Eliminar de base de datos
            if self.db.delete_record(self.table_name, user_id, 'user_id'):
                return {
                    'success': True,
                    'message': 'Usuario eliminado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al eliminar el usuario'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def change_password(self, user_id: str, current_password: str, 
                       new_password: str) -> Dict[str, Any]:
        """
        Cambiar contraseña de usuario
        
        Args:
            user_id: ID del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            Resultado de la operación
        """
        try:
            # Verificar usuario y contraseña actual
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'Usuario no encontrado'
                }
            
            if not self._verify_password(current_password, user['password_hash']):
                return {
                    'success': False,
                    'message': 'Contraseña actual incorrecta'
                }
            
            # Validar nueva contraseña
            if len(new_password) < 6:
                return {
                    'success': False,
                    'message': 'La nueva contraseña debe tener al menos 6 caracteres'
                }
            
            # Actualizar contraseña
            new_hash = self._hash_password(new_password)
            updates = {
                'password_hash': new_hash,
                'password_changed_at': datetime.now().isoformat()
            }
            
            if self.db.update_record(self.table_name, user_id, updates, 'user_id'):
                return {
                    'success': True,
                    'message': 'Contraseña cambiada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al cambiar la contraseña'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """
        Obtener usuarios por rol
        
        Args:
            role: Rol a buscar
            
        Returns:
            Lista de usuarios con el rol especificado
        """
        users = self.get_all_users(active_only=True)
        return [u for u in users if u.get('role') == role.lower()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de usuarios
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            all_users = self.get_all_users()
            active_users = [u for u in all_users if u.get('active', True)]
            
            # Contar por roles
            role_counts = {}
            for user in active_users:
                role = user.get('role', 'user')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            # Calcular logins recientes
            recent_logins = len([u for u in active_users 
                               if u.get('last_login') and 
                               (datetime.now() - datetime.fromisoformat(u['last_login'])).days <= 7])
            
            return {
                'total_users': len(all_users),
                'active_users': len(active_users),
                'inactive_users': len(all_users) - len(active_users),
                'role_distribution': role_counts,
                'recent_logins': recent_logins,
                'admin_count': role_counts.get('admin', 0),
                'teacher_count': role_counts.get('teacher', 0),
                'user_count': role_counts.get('user', 0)
            }
            
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {}
    
    def _validate_user_data(self, username: str, full_name: str, 
                           email: str, password: str) -> Dict[str, Any]:
        """
        Validar datos de usuario
        
        Args:
            username: Nombre de usuario
            full_name: Nombre completo
            email: Email
            password: Contraseña
            
        Returns:
            Resultado de validación
        """
        # Validar username
        if not username or len(username.strip()) < 3:
            return {
                'valid': False,
                'message': 'El nombre de usuario debe tener al menos 3 caracteres'
            }
        
        if len(username.strip()) > 50:
            return {
                'valid': False,
                'message': 'El nombre de usuario no puede exceder 50 caracteres'
            }
        
        # Validar nombre completo
        if not full_name or len(full_name.strip()) < 2:
            return {
                'valid': False,
                'message': 'El nombre completo debe tener al menos 2 caracteres'
            }
        
        # Validar email
        if not email or len(email.strip()) < 5:
            return {
                'valid': False,
                'message': 'Email requerido'
            }
        
        import re
        if not re.match(config.EMAIL_PATTERN, email.strip()):
            return {
                'valid': False,
                'message': 'Email no válido'
            }
        
        # Validar contraseña
        if not password or len(password) < 6:
            return {
                'valid': False,
                'message': 'La contraseña debe tener al menos 6 caracteres'
            }
        
        return {'valid': True, 'message': 'Datos válidos'}
    
    def _generate_user_id(self) -> str:
        """
        Generar ID único para usuario
        
        Returns:
            ID único generado
        """
        return f"USER_{str(uuid.uuid4())[:8].upper()}"
    
    def _hash_password(self, password: str) -> str:
        """
        Crear hash de contraseña
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        # Usar SHA-256 con salt
        salt = "AsistoYA_Salt_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verificar contraseña contra hash
        
        Args:
            password: Contraseña en texto plano
            password_hash: Hash almacenado
            
        Returns:
            True si la contraseña es correcta
        """
        return self._hash_password(password) == password_hash
    
    def _update_login_info(self, user_id: str):
        """
        Actualizar información de login
        
        Args:
            user_id: ID del usuario
        """
        try:
            user = self.get_user_by_id(user_id)
            if user:
                login_count = user.get('login_count', 0) + 1
                updates = {
                    'last_login': datetime.now().isoformat(),
                    'login_count': login_count
                }
                self.db.update_record(self.table_name, user_id, updates, 'user_id')
        except Exception as e:
            print(f"Error updating login info: {e}")

# Crear instancia global del modelo de usuarios
user_model = UserModel()
