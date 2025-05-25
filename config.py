#!/usr/bin/env python3
"""
AsistoYA - Archivo de Configuración Principal
Configuraciones centralizadas para todo el sistema
"""

import os
from datetime import datetime

# ================================
# CONFIGURACIONES GENERALES
# ================================

# Información del proyecto
PROJECT_NAME = "AsistoYA"
PROJECT_VERSION = "2.0"
PROJECT_DESCRIPTION = "Sistema de Asistencia con Reconocimiento Facial"

# Configuraciones de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(BASE_DIR, "faces")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

# Crear directorios si no existen
for directory in [DATA_DIR, FACES_DIR, REPORTS_DIR, BACKUP_DIR]:
    os.makedirs(directory, exist_ok=True)

# ================================
# CONFIGURACIONES DE BASE DE DATOS
# ================================

# Archivos de datos JSON
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.json")
CLASSROOMS_FILE = os.path.join(DATA_DIR, "classrooms.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Archivos del modelo de reconocimiento facial
FACE_MODEL_FILE = os.path.join(DATA_DIR, "face_model.yml")
NAMES_DICT_FILE = os.path.join(DATA_DIR, "names_dict.json")

# ================================
# CONFIGURACIONES DE RECONOCIMIENTO FACIAL
# ================================

# Configuraciones de OpenCV
DEFAULT_CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FACE_SIZE = (150, 150)

# Configuraciones del detector de rostros
HAAR_CASCADE_FILE = "haarcascade_frontalface_default.xml"
DETECTION_SCALE_FACTOR = 1.3
DETECTION_MIN_NEIGHBORS = 5
DETECTION_MIN_SIZE = (50, 50)

# Configuraciones del reconocizador LBPH
LBPH_RADIUS = 1
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8

# Umbrales y configuraciones
DEFAULT_CONFIDENCE_THRESHOLD = 85.0  # Porcentaje de confianza mínimo
MIN_CONFIDENCE_THRESHOLD = 50.0
MAX_CONFIDENCE_THRESHOLD = 95.0

# Configuraciones de registro
FACES_PER_STUDENT = 5  # Número de rostros a capturar por estudiante
FACE_CAPTURE_INTERVAL = 1.0  # Segundos entre capturas

# Configuraciones de cooldown
DEFAULT_ATTENDANCE_COOLDOWN = 30  # Segundos entre registros del mismo estudiante
MIN_COOLDOWN = 5
MAX_COOLDOWN = 60

# ================================
# CONFIGURACIONES DE INTERFAZ GRÁFICA
# ================================

# Configuraciones de la ventana principal
WINDOW_TITLE = f"{PROJECT_NAME} v{PROJECT_VERSION}"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Colores de la interfaz
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Configuraciones de estilo
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_SIZE_TITLE = 14

# ================================
# CONFIGURACIONES DE REPORTES
# ================================

# Formatos de fecha y hora
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configuraciones de exportación
CSV_ENCODING = "utf-8"
CSV_DELIMITER = ","

# ================================
# CONFIGURACIONES DE LOGGING
# ================================

# Configuraciones de logs
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ================================
# CONFIGURACIONES POR DEFECTO
# ================================

# Configuraciones predeterminadas del sistema
DEFAULT_SETTINGS = {
    "confidence_threshold": DEFAULT_CONFIDENCE_THRESHOLD,
    "attendance_cooldown": DEFAULT_ATTENDANCE_COOLDOWN,
    "camera_index": DEFAULT_CAMERA_INDEX,
    "auto_backup": True,
    "backup_interval": 24,  # horas
    "face_detection_enabled": True,
    "sound_notifications": True,
    "theme": "light",
    "language": "es"
}

# Aula predeterminada
DEFAULT_CLASSROOM = {
    "classroom_id": "AULA_001",
    "name": "Aula Principal",
    "description": "Aula predeterminada del sistema",
    "capacity": 30,
    "location": "Edificio Principal",
    "active": True,
    "created_at": datetime.now().isoformat()
}

# Usuario administrador predeterminado
DEFAULT_ADMIN_USER = {
    "user_id": "ADMIN_001",
    "username": "admin",
    "full_name": "Administrador del Sistema",
    "email": "admin@asistoya.local",
    "role": "admin",
    "active": True,
    "created_at": datetime.now().isoformat()
}

# ================================
# CONFIGURACIONES DE VALIDACIÓN
# ================================

# Validaciones de entrada
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
MIN_EMAIL_LENGTH = 5
MAX_EMAIL_LENGTH = 254

# Patrones de validación
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
STUDENT_ID_PATTERN = r'^[A-Z]{2}[0-9]{4}$'

# ================================
# CONFIGURACIONES DE RENDIMIENTO
# ================================

# Configuraciones de cache
CACHE_SIZE = 100
CACHE_TTL = 300  # segundos

# Configuraciones de procesamiento
MAX_CONCURRENT_RECOGNITIONS = 3
PROCESSING_TIMEOUT = 30  # segundos

# Configuraciones de memoria
MAX_MEMORY_USAGE = 512  # MB
CLEANUP_INTERVAL = 300  # segundos

# ================================
# FUNCIONES DE UTILIDAD
# ================================

def get_config_value(key, default=None):
    """Obtener un valor de configuración por clave"""
    return globals().get(key, default)

def set_config_value(key, value):
    """Establecer un valor de configuración"""
    globals()[key] = value

def get_file_path(filename, directory=DATA_DIR):
    """Obtener la ruta completa de un archivo"""
    return os.path.join(directory, filename)

def ensure_directory_exists(directory):
    """Asegurar que un directorio existe"""
    os.makedirs(directory, exist_ok=True)
    return directory

def get_timestamp():
    """Obtener timestamp actual en formato estándar"""
    return datetime.now().strftime(DATETIME_FORMAT)

def get_date_string():
    """Obtener fecha actual en formato estándar"""
    return datetime.now().strftime(DATE_FORMAT)

def get_time_string():
    """Obtener hora actual en formato estándar"""
    return datetime.now().strftime(TIME_FORMAT)

# ================================
# INICIALIZACIÓN
# ================================

def initialize_config():
    """Inicializar configuraciones del sistema"""
    # Crear directorios necesarios
    for directory in [DATA_DIR, FACES_DIR, REPORTS_DIR, BACKUP_DIR]:
        ensure_directory_exists(directory)
    
    # Verificar archivos críticos
    required_files = [
        STUDENTS_FILE,
        ATTENDANCE_FILE,
        CLASSROOMS_FILE,
        USERS_FILE,
        SETTINGS_FILE
    ]
    
    # Crear archivos vacíos si no existen
    for file_path in required_files:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    f.write('[]')
    
    return True

# Inicializar configuraciones al importar el módulo
if __name__ != "__main__":
    initialize_config()

# ================================
# INFORMACIÓN DE DEBUG
# ================================

if __name__ == "__main__":
    print(f"=== {PROJECT_NAME} v{PROJECT_VERSION} - Configuración ===")
    print(f"Directorio base: {BASE_DIR}")
    print(f"Directorio de datos: {DATA_DIR}")
    print(f"Directorio de rostros: {FACES_DIR}")
    print(f"Directorio de reportes: {REPORTS_DIR}")
    print(f"Inicialización completada: {initialize_config()}")
