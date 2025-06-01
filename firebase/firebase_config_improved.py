"""
🔥 Firebase Configuration Improved - AsistoYA
Configuración optimizada con credenciales reales y fallback local
"""

import json
import os
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configuración de Firebase usando datos reales del proyecto
FIREBASE_CONFIG = {
    "project_id": "un-estudiante-kgft8a",
    "project_number": "446425771909",
    "storage_bucket": "un-estudiante-kgft8a.appspot.com",
    "api_key": "AIzaSyCnNcBEZ3-XgdgMcBirlAQfmmeI4Hqhp_k",
    "auth_domain": "un-estudiante-kgft8a.firebaseapp.com",
    "database_url": f"https://un-estudiante-kgft8a-default-rtdb.firebaseio.com/",
    "messaging_sender_id": "446425771909",
    "app_id": "1:446425771909:android:1c0cd10fbfb3b088459eec"
}

class FirebaseManager:
    """Gestor mejorado de Firebase con fallback local"""
    
    def __init__(self):
        self.config = FIREBASE_CONFIG
        self.firebase_app = None
        self.firestore_db = None
        self.storage_bucket = None
        self.auth_client = None
        self.local_mode = True
        self.logger = self._setup_logger()
        
        # Directorio para datos locales
        self.local_data_dir = Path(__file__).parent.parent / "data" / "firebase_sync"
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self):
        """Configurar logging"""
        logger = logging.getLogger('FirebaseManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '🔥 %(asctime)s - Firebase - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def initialize(self) -> bool:
        """Inicializar Firebase con fallback automático"""
        try:
            # Intentar inicialización con Firebase Admin SDK
            if self._initialize_firebase_admin():
                self.local_mode = False
                self.logger.info("✅ Firebase Admin SDK inicializado correctamente")
                return True
            
            # Si falla, usar modo local con sincronización
            self.logger.info("🔧 Iniciando en modo local con sincronización programada")
            self._initialize_local_mode()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en inicialización: {e}")
            self._initialize_local_mode()
            return True
    
    def _initialize_firebase_admin(self) -> bool:
        """Intentar inicializar Firebase Admin SDK"""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore, storage
            
            # Verificar si ya está inicializado
            if firebase_admin._apps:
                self.firebase_app = firebase_admin.get_app()
                self.firestore_db = firestore.client()
                self.storage_bucket = storage.bucket()
                return True
            
            # Buscar credenciales válidas
            service_account_path = self._find_valid_credentials()
            if not service_account_path:
                return False
            
            # Inicializar Firebase Admin
            cred = credentials.Certificate(str(service_account_path))
            self.firebase_app = firebase_admin.initialize_app(cred, {
                'storageBucket': self.config['storage_bucket'],
                'projectId': self.config['project_id']
            })
            
            self.firestore_db = firestore.client()
            self.storage_bucket = storage.bucket()
            
            # Probar conexión
            return self._test_firebase_connection()
            
        except ImportError:
            self.logger.warning("⚠️ Firebase Admin SDK no está instalado")
            return False
        except Exception as e:
            self.logger.warning(f"⚠️ Error inicializando Firebase Admin: {e}")
            return False
    
    def _find_valid_credentials(self) -> Optional[Path]:
        """Buscar archivo de credenciales válido"""
        credential_files = [
            "service-account-real.json",  # Archivo preferido para credenciales reales
            "service-account-key.json",   # Credenciales demo
            "firebase-service-account.json"  # Credenciales ejemplo
        ]
        
        for filename in credential_files:
            file_path = Path(__file__).parent / filename
            if file_path.exists():
                if self._validate_credentials(file_path):
                    self.logger.info(f"🔑 Usando credenciales: {filename}")
                    return file_path
                else:
                    self.logger.warning(f"⚠️ Credenciales inválidas en: {filename}")
        
        return None
    
    def _validate_credentials(self, cred_path: Path) -> bool:
        """Validar archivo de credenciales"""
        try:
            with open(cred_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            
            # Verificar campos obligatorios
            required_fields = ['type', 'project_id', 'client_email']
            if not all(field in creds for field in required_fields):
                return False
            
            # Verificar que sea service account
            if creds.get('type') != 'service_account':
                return False
            
            # Verificar project_id correcto
            if creds.get('project_id') != self.config['project_id']:
                self.logger.warning(f"⚠️ Project ID no coincide: {creds.get('project_id')}")
                return False
            
            # Permitir credenciales demo para desarrollo
            if 'demo' in creds.get('client_email', '').lower():
                self.logger.info("🧪 Detectadas credenciales de desarrollo")
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validando credenciales: {e}")
            return False
    
    def _test_firebase_connection(self) -> bool:
        """Probar conexión a Firebase"""
        try:
            if self.firestore_db:
                # Intentar operación simple
                test_ref = self.firestore_db.collection('_connection_test')
                test_ref.document('test').set({
                    'timestamp': datetime.now().isoformat(),
                    'status': 'connected'
                })
                self.logger.info("✅ Conexión a Firestore verificada")
                return True
        except Exception as e:
            self.logger.warning(f"⚠️ Prueba de conexión falló: {e}")
            return False
        return False
    
    def _initialize_local_mode(self):
        """Inicializar modo local"""
        self.local_mode = True
        self.firebase_app = None
        self.firestore_db = None
        self.storage_bucket = None
        
        # Crear estructura de datos locales
        (self.local_data_dir / "attendance").mkdir(exist_ok=True)
        (self.local_data_dir / "students").mkdir(exist_ok=True)
        (self.local_data_dir / "reports").mkdir(exist_ok=True)
        (self.local_data_dir / "sync_queue").mkdir(exist_ok=True)
        
        self.logger.info("🏠 Modo local inicializado")
    
    def save_attendance_record(self, record: Dict[str, Any]) -> bool:
        """Guardar registro de asistencia"""
        try:
            record_id = f"{record.get('student_id', 'unknown')}_{int(datetime.now().timestamp())}"
            
            if not self.local_mode and self.firestore_db:
                # Guardar en Firebase
                doc_ref = self.firestore_db.collection('attendance_records').document(record_id)
                doc_ref.set(record)
                self.logger.info(f"✅ Registro guardado en Firebase: {record_id}")
            else:
                # Guardar localmente
                self._save_local_record('attendance', record_id, record)
                self.logger.info(f"💾 Registro guardado localmente: {record_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando registro: {e}")
            # Fallback a local siempre
            try:
                record_id = f"{record.get('student_id', 'unknown')}_{int(datetime.now().timestamp())}"
                self._save_local_record('attendance', record_id, record)
                self.logger.info(f"💾 Guardado en fallback local: {record_id}")
                return True
            except Exception as e2:
                self.logger.error(f"❌ Error en fallback local: {e2}")
                return False
    
    def get_attendance_records(self, filters: Dict[str, Any] = None) -> list:
        """Obtener registros de asistencia"""
        try:
            if not self.local_mode and self.firestore_db:
                # Obtener de Firebase
                return self._get_firebase_records('attendance_records', filters)
            else:
                # Obtener de archivos locales
                return self._get_local_records('attendance', filters)
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo registros: {e}")
            return []
    
    def save_student_data(self, student_id: str, student_data: Dict[str, Any]) -> bool:
        """Guardar datos de estudiante"""
        try:
            if not self.local_mode and self.firestore_db:
                doc_ref = self.firestore_db.collection('students').document(student_id)
                doc_ref.set(student_data)
                self.logger.info(f"✅ Estudiante guardado en Firebase: {student_id}")
            else:
                self._save_local_record('students', student_id, student_data)
                self.logger.info(f"💾 Estudiante guardado localmente: {student_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando estudiante: {e}")
            return False
    
    def _save_local_record(self, collection: str, record_id: str, data: Dict[str, Any]):
        """Guardar registro local"""
        file_path = self.local_data_dir / collection / f"{record_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        # Agregar a cola de sincronización
        self._queue_for_sync(collection, record_id, data)
    
    def _get_local_records(self, collection: str, filters: Dict[str, Any] = None) -> list:
        """Obtener registros locales"""
        records = []
        collection_dir = self.local_data_dir / collection
        
        if not collection_dir.exists():
            return records
        
        for file_path in collection_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                    record['id'] = file_path.stem
                    
                    # Aplicar filtros si se proporcionan
                    if self._matches_filters(record, filters):
                        records.append(record)
            except Exception as e:
                self.logger.warning(f"⚠️ Error leyendo archivo {file_path}: {e}")
        
        return records
    
    def _get_firebase_records(self, collection: str, filters: Dict[str, Any] = None) -> list:
        """Obtener registros de Firebase"""
        records = []
        try:
            collection_ref = self.firestore_db.collection(collection)
            
            # Aplicar filtros
            query = collection_ref
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            
            docs = query.stream()
            for doc in docs:
                record = doc.to_dict()
                record['id'] = doc.id
                records.append(record)
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo de Firebase: {e}")
        
        return records
    
    def _matches_filters(self, record: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Verificar si un registro coincide con los filtros"""
        if not filters:
            return True
        
        for field, value in filters.items():
            if record.get(field) != value:
                return False
        
        return True
    
    def _queue_for_sync(self, collection: str, record_id: str, data: Dict[str, Any]):
        """Agregar registro a cola de sincronización"""
        try:
            sync_item = {
                'collection': collection,
                'record_id': record_id,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'synced': False
            }
            
            sync_file = self.local_data_dir / "sync_queue" / f"{collection}_{record_id}.json"
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_item, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error agregando a cola de sync: {e}")
    
    def sync_pending_records(self) -> int:
        """Sincronizar registros pendientes con Firebase"""
        if self.local_mode or not self.firestore_db:
            self.logger.info("🔄 Sincronización omitida (modo local)")
            return 0
        
        sync_queue_dir = self.local_data_dir / "sync_queue"
        synced_count = 0
        
        for sync_file in sync_queue_dir.glob("*.json"):
            try:
                with open(sync_file, 'r', encoding='utf-8') as f:
                    sync_item = json.load(f)
                
                if sync_item.get('synced'):
                    continue
                
                # Intentar sincronizar
                collection = sync_item['collection']
                record_id = sync_item['record_id']
                data = sync_item['data']
                
                if collection == 'attendance':
                    doc_ref = self.firestore_db.collection('attendance_records').document(record_id)
                elif collection == 'students':
                    doc_ref = self.firestore_db.collection('students').document(record_id)
                else:
                    continue
                
                doc_ref.set(data)
                
                # Marcar como sincronizado
                sync_item['synced'] = True
                sync_item['sync_timestamp'] = datetime.now().isoformat()
                
                with open(sync_file, 'w', encoding='utf-8') as f:
                    json.dump(sync_item, f, indent=2, ensure_ascii=False, default=str)
                
                synced_count += 1
                self.logger.info(f"🔄 Sincronizado: {collection}/{record_id}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error sincronizando {sync_file}: {e}")
        
        if synced_count > 0:
            self.logger.info(f"✅ {synced_count} registros sincronizados")
        
        return synced_count
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Obtener estado de conexión"""
        return {
            'firebase_connected': not self.local_mode,
            'local_mode': self.local_mode,
            'project_id': self.config['project_id'],
            'has_firestore': self.firestore_db is not None,
            'has_storage': self.storage_bucket is not None,
            'local_data_dir': str(self.local_data_dir)
        }

# Instancia global
_firebase_manager = None

def get_firebase_manager() -> FirebaseManager:
    """Obtener instancia singleton"""
    global _firebase_manager
    if _firebase_manager is None:
        _firebase_manager = FirebaseManager()
    return _firebase_manager

def initialize_firebase() -> bool:
    """Inicializar Firebase globalmente"""
    manager = get_firebase_manager()
    return manager.initialize()
