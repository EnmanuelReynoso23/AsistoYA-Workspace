import hashlib
import os
import base64
from cryptography.fernet import Fernet
import pyotp
import time

class Security:
    def __init__(self):
        self.key = self.load_key()
        self.cipher = Fernet(self.key)
        # Usuario y contraseña de prueba para desarrollo
        self.test_users = {
            "admin": self.hash_password("admin123")
        }

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
