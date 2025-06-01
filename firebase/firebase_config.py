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
from datetime import datetime

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
            # Verificar si Firebase ya está inicializado
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                self.db = firestore.client()
                self.bucket = storage.bucket()
                self.logger.info("✅ Firebase ya estaba inicializado")
                return True
            
            # Buscar archivos de credenciales en orden de prioridad
            credential_files = [
                "service-account-key.json",
                "firebase-service-account.json",
                "service-account-demo.json"
            ]
            
            cred_path = None
            for filename in credential_files:
                test_path = Path(__file__).parent / filename
                if test_path.exists():
                    cred_path = test_path
                    self.logger.info(f"🔥 Usando credenciales: {filename}")
                    break
            
            if not cred_path or not cred_path.exists():
                self.logger.warning(f"⚠️ Archivo de credenciales no encontrado")
                return self._initialize_without_credentials()
            
            # Validar archivo de credenciales
            if not self._validate_credentials_file(cred_path):
                self.logger.warning("⚠️ Credenciales inválidas, usando modo local")
                return self._initialize_without_credentials()
            
            # Inicializar Firebase Admin SDK
            cred = credentials.Certificate(str(cred_path))
            
            self.app = firebase_admin.initialize_app(cred, {
                'storageBucket': self.storage_bucket,
                'projectId': self.project_id
            })
            
            # Inicializar servicios
            self.db = firestore.client()
            self.bucket = storage.bucket()
            
            # Probar conexión
            if self._test_connection():
                self.logger.info("✅ Firebase inicializado correctamente")
                return True
            else:
                self.logger.warning("⚠️ Conexión fallida, usando modo local")
                return self._initialize_without_credentials()
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Firebase: {e}")
            return self._initialize_without_credentials()
    
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
    
    def _validate_credentials_file(self, cred_path: Path) -> bool:
        """Validar archivo de credenciales"""
        try:
            with open(cred_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            
            # Si es google-services.json, validar estructura diferente
            if cred_path.name == "google-services.json":
                required_keys = ['project_info']
                return all(key in creds for key in required_keys)
            
            # Para service account, verificar campos obligatorios
            required_fields = [
                'type', 'project_id', 'client_email'
            ]
            
            for field in required_fields:
                if field not in creds:
                    self.logger.warning(f"⚠️ Campo faltante: {field}")
                    if field == 'type':
                        return False  # type es crítico
            
            # Verificar que sea service account
            if creds.get('type') != 'service_account':
                self.logger.error("❌ Debe ser tipo 'service_account'")
                return False
            
            # Permitir credenciales de demo para desarrollo
            if (creds.get('private_key_id') == 'demo_key_id_12345' or
                'demo' in creds.get('client_email', '').lower()):
                self.logger.warning("⚠️ Usando credenciales de DEMO")
                return True  # Permitir credenciales demo
            
            # Verificar que no sean valores de ejemplo antiguos
            if (creds.get('private_key_id') == 'sample12345678901234567890' or
                'sample' in creds.get('private_key', '').lower() or
                creds.get('client_id') == '123456789012345678901'):
                self.logger.error("❌ Detectadas credenciales de ejemplo inválidas")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validando credenciales: {e}")
            return False
    
    def _test_connection(self) -> bool:
        """Probar conexión a Firebase"""
        try:
            if self.db:
                # Intentar una operación simple
                test_ref = self.db.collection('_test_connection')
                test_ref.document('test').set({'timestamp': datetime.now().isoformat()})
                return True
        except Exception as e:
            self.logger.warning(f"⚠️ Prueba de conexión falló: {e}")
            return False
        return False
    
    def _initialize_without_credentials(self) -> bool:
        """Inicializar en modo local sin Firebase"""
        try:
            self.logger.info("🔧 Iniciando en modo local (sin Firebase)")
            self.app = None
            self.db = None
            self.bucket = None
            
            # Crear directorio local para datos
            local_data_dir = Path(__file__).parent.parent / "data" / "firebase_local"
            local_data_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("✅ Modo local inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en modo local: {e}")
            return False
        
    def _initialize_from_google_services(self, google_services_path):
        """Inicializar Firebase usando google-services.json"""
        try:
            import json
            
            with open(google_services_path, 'r') as f:
                config = json.load(f)
            
            # Extraer información del proyecto
            project_info = config.get('project_info', {})
            project_id = project_info.get('project_id', self.project_id)
            storage_bucket = project_info.get('storage_bucket', self.storage_bucket)
            
            # Actualizar configuración
            self.project_id = project_id
            self.storage_bucket = storage_bucket
            
            # Para google-services.json necesitamos crear credenciales temporales
            # o usar modo sin credenciales pero con la configuración correcta
            self.logger.info(f"✅ Configuración extraída de google-services.json")
            self.logger.info(f"📦 Project ID: {project_id}")
            self.logger.info(f"🗄️ Storage Bucket: {storage_bucket}")
            
            # Inicializar en modo local con configuración correcta
            return self._initialize_without_credentials()
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando google-services.json: {e}")
            return False

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
