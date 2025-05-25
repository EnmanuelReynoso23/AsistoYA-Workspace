#!/usr/bin/env python3
"""
AsistoYA - Módulo de Reconocimiento Facial
Sistema completo de reconocimiento facial para asistencia
"""

# Información del módulo
__version__ = "2.0"
__author__ = "AsistoYA Team"
__description__ = "Sistema de reconocimiento facial para control de asistencia"

# Importaciones principales
from . import camera_manager
from . import face_detector
from . import face_recognizer
from . import recognition_system

# Exportar clases principales
try:
    from .camera_manager import CameraManager
    from .face_detector import FaceDetector
    from .face_recognizer import FaceRecognizer
    from .recognition_system import FaceRecognitionSystem
except ImportError as e:
    # En caso de error de importación, continuar sin errores
    print(f"Warning: Could not import some face recognition modules: {e}")

__all__ = [
    'CameraManager',
    'FaceDetector', 
    'FaceRecognizer',
    'FaceRecognitionSystem'
]

# Configuraciones por defecto
DEFAULT_CONFIG = {
    'camera_index': 0,
    'frame_width': 640,
    'frame_height': 480,
    'detection_scale_factor': 1.3,
    'detection_min_neighbors': 5,
    'confidence_threshold': 85.0,
    'face_size': (150, 150)
}

def get_version():
    """Obtener versión del módulo"""
    return __version__

def get_default_config():
    """Obtener configuración por defecto"""
    return DEFAULT_CONFIG.copy()
