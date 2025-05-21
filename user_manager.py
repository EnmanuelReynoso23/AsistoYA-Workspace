import hashlib

class UserManager:
    def __init__(self):
        # Diccionario en memoria: {username: password_hash}
        self.users = {}

    def register_user(self, username, password):
        if not username or not password:
            return False, "Usuario y contraseña requeridos."
        if username in self.users:
            return False, "El usuario ya existe."
        self.users[username] = self._hash_password(password)
        return True, "Usuario registrado exitosamente."

    def authenticate(self, username, password):
        if username not in self.users:
            return False
        return self.users[username] == self._hash_password(password)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def list_users(self):
        return list(self.users.keys())
