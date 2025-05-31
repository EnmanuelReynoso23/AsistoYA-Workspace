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
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando notificación: {e}")
            return False
    
    def upload_image(self, image_path: str, remote_path: str) -> str:
        """Subir imagen a Firebase Storage"""
        try:
            bucket = self.get_storage_bucket()
            blob = bucket.blob(remote_path)
            
            with open(image_path, 'rb') as image_file:
                blob.upload_from_file(image_file)
            
            # Hacer público el archivo
            blob.make_public()
            
            self.logger.info(f"✅ Imagen subida: {remote_path}")
            return blob.public_url
            
        except Exception as e:
            self.logger.error(f"❌ Error subiendo imagen: {e}")
            return ""
    
    def save_attendance_record(self, record: dict) -> bool:
        """Guardar registro de asistencia en Firestore"""
        try:
            db = self.get_firestore_client()
            collection_ref = db.collection('attendance_records')
            doc_ref = collection_ref.add(record)
            
            self.logger.info(f"✅ Registro guardado: {doc_ref[1].id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando registro: {e}")
            return False
    
    def get_attendance_records(self, filters: dict = None) -> list:
        """Obtener registros de asistencia desde Firestore"""
        try:
            db = self.get_firestore_client()
            collection_ref = db.collection('attendance_records')
            
            # Aplicar filtros si se proporcionan
            query = collection_ref
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            
            docs = query.stream()
            records = []
            
            for doc in docs:
                record = doc.to_dict()
                record['id'] = doc.id
                records.append(record)
            
            self.logger.info(f"✅ {len(records)} registros obtenidos")
            return records
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo registros: {e}")
            return []

# Instancia global singleton
_firebase_instance = None

def get_firebase() -> FirebaseConfig:
    """Obtener instancia singleton de Firebase"""
    global _firebase_instance
    if _firebase_instance is None:
        _firebase_instance = FirebaseConfig()
    return _firebase_instance

# Función de conveniencia para inicialización
def initialize_firebase() -> bool:
    """Inicializar Firebase globalmente"""
    firebase = get_firebase()
    return firebase.initialize()
