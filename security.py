import hashlib
import os
import base64
from cryptography.fernet import Fernet
import pyotp
import time
import random
import string
import json

class Security:
    def __init__(self):
        self.key = self.load_key()
        self.cipher = Fernet(self.key)
        # Usuario y contraseña de prueba para desarrollo
        self.test_users = {
            "admin": self.hash_password("admin123")
        }
        # Inicializar el almacenamiento de códigos de acceso para tutores
        self.tutor_access_codes = self.load_tutor_access_codes()

    def load_key(self):
        key_file = "secret.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as file:
                key = file.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as file:
                file.write(key)
        return key

    def encrypt_data(self, data):
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data):
        decrypted_data = self.cipher.decrypt(base64.urlsafe_b64decode(encrypted_data.encode()))
        return decrypted_data.decode()

    def hash_password(self, password):
        salt = os.urandom(16)
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.urlsafe_b64encode(salt + hashed_password).decode()

    def verify_password(self, stored_password, provided_password):
        decoded_password = base64.urlsafe_b64decode(stored_password.encode())
        salt = decoded_password[:16]
        stored_hash = decoded_password[16:]
        provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
        return stored_hash == provided_hash

    def authenticate(self, username, password):
        """Authenticate a user with username and password"""
        if username in self.test_users:
            return self.verify_password(self.test_users[username], password)
        return False

    def enforce_data_retention_policy(self, data, retention_period):
        current_time = int(time.time())
        return [item for item in data if current_time - item['timestamp'] <= retention_period]

    def enable_two_factor_authentication(self, user):
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        user.save()
        return secret

    def verify_two_factor_code(self, user, code):
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code)
        
    def generate_tutor_access_code(self, student_id, course_id=None, expiration_hours=24):
        """
        Genera un código único para acceso de tutores
        
        Args:
            student_id (str): ID del estudiante al que está relacionado el tutor
            course_id (str, optional): ID del curso específico (o None para todos)
            expiration_hours (int): Horas de validez del código
            
        Returns:
            str: Código de acceso generado
        """
        # Generar código alfanumérico de 8 caracteres
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(characters) for _ in range(8))
        
        # Configurar los datos del código
        expiration_time = int(time.time()) + (expiration_hours * 60 * 60)
        code_data = {
            'code': code,
            'student_id': student_id,
            'course_id': course_id,
            'expiration': expiration_time,
            'is_used': False
        }
        
        # Guardar el código en el almacén
        self.tutor_access_codes[code] = code_data
        self.save_tutor_access_codes()
        
        return code
    
    def validate_tutor_access_code(self, provided_code):
        """
        Valida un código de acceso de tutor y marca como usado
        
        Args:
            provided_code (str): Código proporcionado por el tutor
            
        Returns:
            dict or None: Datos asociados al código si es válido, None en caso contrario
        """
        # Verificar si el código existe
        if provided_code not in self.tutor_access_codes:
            return None
            
        code_data = self.tutor_access_codes[provided_code]
        
        # Verificar si el código ya fue usado
        if code_data['is_used']:
            return None
            
        # Verificar si el código no ha expirado
        current_time = int(time.time())
        if current_time > code_data['expiration']:
            return None
            
        # Marcar el código como usado
        code_data['is_used'] = True
        code_data['used_at'] = current_time
        self.save_tutor_access_codes()
        
        return code_data
    
    def get_student_access_codes(self, student_id):
        """
        Obtiene todos los códigos generados para un estudiante
        
        Args:
            student_id (str): ID del estudiante
            
        Returns:
            list: Lista de códigos asociados al estudiante
        """
        result = []
        for code, data in self.tutor_access_codes.items():
            if data['student_id'] == student_id:
                result.append(data)
        return result
    
    def load_tutor_access_codes(self):
        """Carga los códigos de acceso de tutores desde un archivo"""
        try:
            if os.path.exists('data/tutor_access_codes.json'):
                with open('data/tutor_access_codes.json', 'r') as file:
                    return json.load(file)
            else:
                return {}
        except Exception as e:
            print(f"Error loading tutor access codes: {e}")
            return {}
    
    def save_tutor_access_codes(self):
        """Guarda los códigos de acceso de tutores en un archivo"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/tutor_access_codes.json', 'w') as file:
                json.dump(self.tutor_access_codes, file)
        except Exception as e:
            print(f"Error saving tutor access codes: {e}")
