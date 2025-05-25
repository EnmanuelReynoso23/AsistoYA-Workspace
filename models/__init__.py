#!/usr/bin/env python3
"""
AsistoYA - Modelos del Sistema
Módulos de gestión de datos y modelos del sistema
"""

# Información del módulo
__version__ = "2.0"
__author__ = "AsistoYA Team"
__description__ = "Modelos de datos para el sistema AsistoYA"

# Importaciones principales
from . import database
from . import user_model
from . import student_model
from . import classroom_model
from . import attendance_model

# Exportar clases principales
try:
    from .database import DatabaseManager
    from .user_model import UserModel
    from .student_model import StudentModel
    from .classroom_model import ClassroomModel
    from .attendance_model import AttendanceModel
except ImportError as e:
    # En caso de error de importación, continuar sin errores
    print(f"Warning: Could not import some models: {e}")

__all__ = [
    'DatabaseManager',
    'UserModel',
    'StudentModel',
    'ClassroomModel',
    'AttendanceModel'
]
