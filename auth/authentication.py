"""
🔐 Sistema de Autenticación Empresarial - AsistoYA
Autenticación multi-nivel con encriptación avanzada
"""

import hashlib
import json
import jwt
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
import logging
from typing import Optional, Dict, List

class AuthManager:
    """Gestor de autenticación empresarial"""
    
    # Roles del sistema
    ROLES = {
        'SUPER_ADMIN': 'super_admin',
        'ADMIN': 'admin', 
        'TEACHER': 'teacher',
        'SUPERVISOR': 'supervisor'
    }
    
    # Permisos por rol
    PERMISSIONS = {
        'super_admin': [
            'manage_users', 'manage_students', 'manage_attendance',
            'view_reports', 'export_data', 'system_config', 'manage_backup'
        ],
        'admin': [
            'manage_students', 'manage_attendance', 'view_reports', 
            'export_data', 'system_config'
        ],
        'teacher': [
            'manage_students', 'manage_attendance', 'view_reports'
        ],
        'supervisor': [
            'view_reports', 'manage_attendance'
        ]
    }
    
    def __init__(self):
        self.data_dir = Path("data/auth")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.data_dir / "users.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self.key_file = self.data_dir / "encryption.key"
        
        self.logger = self._setup_logger()
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self.jwt_secret = self._get_jwt_secret()
        
        # Crear admin por defecto si no existe
        self._create_default_admin()
    
    def _setup_logger(self):
        """Configurar logging de seguridad"""
        logger = logging.getLogger('Auth')
        logger.setLevel(logging.INFO)
        
        # Crear archivo de logs de seguridad
        log_file = self.data_dir / "security.log"
        file_handler = logging.FileHandler(log_file)
        
        formatter = logging.Formatter(
            '🔐 %(asctime)s - AUTH - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _get_or_create_key(self) -> bytes:
        """Obtener o crear clave de encriptación"""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            self.logger.info("🔑 Nueva clave de encriptación generada")
            return key
    
    def _get_jwt_secret(self) -> str:
        """Obtener secreto JWT"""
        return hashlib.sha256(self.encryption_key).hexdigest()
    
    def _load_users(self) -> Dict:
        """Cargar usuarios encriptados"""
        if not self.users_file.exists():
            return {}
        
        try:
            encrypted_data = self.users_file.read_bytes()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            self.logger.error(f"❌ Error cargando usuarios: {e}")
            return {}
    
    def _save_users(self, users: Dict):
        """Guardar usuarios encriptados"""
        try:
            json_data = json.dumps(users, indent=2).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            self.users_file.write_bytes(encrypted_data)
            self.logger.info("💾 Usuarios guardados de forma segura")
        except Exception as e:
            self.logger.error(f"❌ Error guardando usuarios: {e}")
    
    def _create_default_admin(self):
        """Crear administrador por defecto"""
        users = self._load_users()
        
        if not users:  # Si no hay usuarios
            admin_password = "admin123"  # Cambiar en producción
            hashed_password = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
            
            admin_user = {
                'username': 'admin',
                'email': 'admin@asistoya.com',
                'password_hash': hashed_password.decode(),
                'role': self.ROLES['SUPER_ADMIN'],
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'full_name': 'Administrador Principal'
            }
            
            users['admin'] = admin_user
            self._save_users(users)
            self.logger.info("👤 Usuario administrador por defecto creado")
    
    def create_user(self, username: str, email: str, password: str, 
                   role: str, full_name: str) -> bool:
        """Crear nuevo usuario"""
        try:
            users = self._load_users()
            
            # Verificar si el usuario ya existe
            if username in users:
                self.logger.warning(f"⚠️ Usuario {username} ya existe")
                return False
            
            # Verificar rol válido
            if role not in self.ROLES.values():
                self.logger.error(f"❌ Rol inválido: {role}")
                return False
            
            # Hash de la contraseña
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            # Crear usuario
            user = {
                'username': username,
                'email': email,
                'password_hash': hashed_password.decode(),
                'role': role,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'full_name': full_name
            }
            
            users[username] = user
            self._save_users(users)
            
            self.logger.info(f"✅ Usuario {username} creado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creando usuario: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Autenticar usuario"""
        try:
            users = self._load_users()
            
            if username not in users:
                self.logger.warning(f"⚠️ Intento de login con usuario inexistente: {username}")
                return None
            
            user = users[username]
            
            # Verificar si el usuario está activo
            if not user.get('is_active', True):
                self.logger.warning(f"⚠️ Intento de login con usuario inactivo: {username}")
                return None
            
            # Verificar contraseña
            if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                # Actualizar último login
                user['last_login'] = datetime.now().isoformat()
                users[username] = user
                self._save_users(users)
                
                self.logger.info(f"✅ Login exitoso: {username}")
                return user
            else:
                self.logger.warning(f"⚠️ Contraseña incorrecta para: {username}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error en autenticación: {e}")
            return None
    
    def generate_token(self, user: Dict) -> str:
        """Generar JWT token"""
        payload = {
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=8),  # Token válido por 8 horas
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        self.logger.info(f"🎫 Token generado para: {user['username']}")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verificar JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("⚠️ Token expirado")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("⚠️ Token inválido")
            return None
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """Verificar permisos de usuario"""
        return permission in self.PERMISSIONS.get(user_role, [])
    
    def get_all_users(self) -> List[Dict]:
        """Obtener todos los usuarios (sin contraseñas)"""
        users = self._load_users()
        safe_users = []
        
        for username, user in users.items():
            safe_user = user.copy()
            safe_user.pop('password_hash', None)  # Remover hash de contraseña
            safe_users.append(safe_user)
        
        return safe_users
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Cambiar contraseña de usuario"""
        try:
            # Primero autenticar con contraseña actual
            user = self.authenticate(username, old_password)
            if not user:
                return False
            
            # Cambiar contraseña
            users = self._load_users()
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            users[username]['password_hash'] = hashed_password.decode()
            self._save_users(users)
            
            self.logger.info(f"🔄 Contraseña cambiada para: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cambiando contraseña: {e}")
            return False

# Singleton instance
auth_manager = AuthManager()

def get_auth_manager():
    """Obtener instancia global del gestor de autenticación"""
    return auth_manager
