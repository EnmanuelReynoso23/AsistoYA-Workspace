"""
🔥 Firebase Configuration - AsistoYA Empresarial
Configuración avanzada para integración Firebase completa
"""

import json
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, storage, messaging
from google.cloud.firestore import Client
import logging

class FirebaseConfig:
    """Configuración y gestión avanzada de Firebase"""
    
    def __init__(self):
        self.project_id = "un-estudiante-kgft8a"
        self.storage_bucket = "un-estudiante-kgft8a.appspot.com"
        self.app = None
        self.db = None
        self.bucket = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Configurar logging avanzado"""
        logger = logging.getLogger('Firebase')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '🔥 %(asctime)s - Firebase - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    def initialize(self):
        """Inicializar Firebase con configuración avanzada"""
        try:
            # Ruta al archivo de credenciales
            cred_path = Path(__file__).parent / "firebase-service-account.json"
            
            if not cred_path.exists():
                raise FileNotFoundError(f"Archivo de credenciales no encontrado: {cred_path}")
            
            # Inicializar Firebase Admin SDK
            cred = credentials.Certificate(str(cred_path))
            
            if not firebase_admin._apps:
                self.app = firebase_admin.initialize_app(cred, {
                    'storageBucket': self.storage_bucket,
                    'projectId': self.project_id
                })
            else:
                self.app = firebase_admin.get_app()
            
            # Inicializar servicios
            self.db = firestore.client()
            self.bucket = storage.bucket()
            
            self.logger.info("✅ Firebase inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Firebase: {e}")
            return False
    
    def get_firestore_client(self) -> Client:
        """Obtener cliente de Firestore"""
        if not self.db:
            self.initialize()
        return self.db
    
    def get_storage_bucket(self):
        """Obtener bucket de Storage"""
        if not self.bucket:
            self.initialize()
        return self.bucket
    
    def send_notification(self, token: str, title: str, body: str, data: dict = None):
        """Enviar notificación FCM avanzada"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#2196F3',
                        sound='default',
                        click_action='FLUTTER_NOTIFICATION_CLICK'
                    ),
                    priority='high'
                )
            )
            
            response = messaging.send(message)
            self.logger.info(f"✅ Notificación enviada: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando notificación: {e}")
            return None
    
    def send_batch_notifications(self, tokens: list, title: str, body: str, data: dict = None):
        """Enviar notificaciones masivas"""
        try:
            messages = []
            for token in tokens:
                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    data=data or {},
                    token=token
                )
                messages.append(message)
            
            response = messaging.send_all(messages)
            self.logger.info(f"✅ Notificaciones masivas enviadas: {response.success_count}/{len(tokens)}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando notificaciones masivas: {e}")
            return None

# Singleton instance
firebase_config = FirebaseConfig()

def get_firebase():
    """Obtener instancia global de Firebase"""
    if not firebase_config.app:
        firebase_config.initialize()
    return firebase_config
