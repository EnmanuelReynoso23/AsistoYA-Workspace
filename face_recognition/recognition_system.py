#!/usr/bin/env python3
"""
AsistoYA - Sistema de Reconocimiento Facial
Sistema integral que combina detección y reconocimiento
"""

import cv2
import numpy as np
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import config

from .camera_manager import CameraManager
from .face_detector import FaceDetector
from .face_recognizer import FaceRecognizer

class FaceRecognitionSystem:
    """Sistema completo de reconocimiento facial para asistencia"""
    
    def __init__(self):
        """Inicializar el sistema de reconocimiento"""
        # Componentes principales
        self.camera_manager = CameraManager()
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer()
        
        # Estado del sistema
        self.is_running = False
        self.recognition_thread = None
        self.last_frame = None
        self.frame_lock = threading.Lock()
        
        # Configuraciones
        self.recognition_interval = config.DEFAULT_RECOGNITION_INTERVAL
        self.auto_attendance = True
        
        # Callbacks
        self.on_face_detected = None
        self.on_face_recognized = None
        self.on_attendance_recorded = None
        self.on_error = None
        
        # Estadísticas
        self.stats = {
            'faces_detected': 0,
            'faces_recognized': 0,
            'attendance_recorded': 0,
            'errors': 0,
            'start_time': None,
            'last_recognition': None
        }
        
        # Cache para evitar reconocimientos duplicados
        self.recognition_cache = {}
        self.cache_timeout = 5.0  # segundos
        
    def initialize(self) -> Dict[str, Any]:
        """
        Inicializar todos los componentes del sistema
        
        Returns:
            Resultado de la inicialización
        """
        result = {
            'success': True,
            'components_ready': {},
            'errors': []
        }
        
        try:
            # Inicializar cámara
            camera_ready = self.camera_manager.initialize_camera()
            result['components_ready']['camera'] = camera_ready
            if not camera_ready:
                result['errors'].append(f"Cámara: {self.camera_manager.error_message}")
            
            # Verificar detector
            detector_ready = self.face_detector.is_ready()
            result['components_ready']['detector'] = detector_ready
            if not detector_ready:
                result['errors'].append(f"Detector: {self.face_detector.error_message}")
            
            # Verificar reconocedor
            recognizer_ready = self.face_recognizer.is_ready()
            result['components_ready']['recognizer'] = recognizer_ready
            if not recognizer_ready:
                result['errors'].append("Reconocedor: Modelo no entrenado")
            
            # Determinar si el sistema está completamente listo
            result['success'] = camera_ready and detector_ready
            result['fully_ready'] = camera_ready and detector_ready and recognizer_ready
            
            if result['success']:
                print("Sistema de reconocimiento facial inicializado")
            else:
                print("Sistema inicializado con advertencias")
                
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Error general: {str(e)}")
        
        return result
    
    def start_recognition(self) -> bool:
        """
        Iniciar el sistema de reconocimiento en tiempo real
        
        Returns:
            True si se inició correctamente
        """
        if self.is_running:
            return True
        
        # Verificar que los componentes estén listos
        init_result = self.initialize()
        if not init_result['success']:
            return False
        
        # Iniciar cámara
        if not self.camera_manager.start_capture():
            return False
        
        # Iniciar hilo de reconocimiento
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()
        
        print("Sistema de reconocimiento iniciado")
        return True
    
    def stop_recognition(self):
        """Detener el sistema de reconocimiento"""
        self.is_running = False
        
        # Detener cámara
        self.camera_manager.stop_capture()
        
        # Esperar a que termine el hilo de reconocimiento
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2.0)
        
        print("Sistema de reconocimiento detenido")
    
    def get_current_frame_with_detections(self) -> Optional[np.ndarray]:
        """
        Obtener frame actual con detecciones dibujadas
        
        Returns:
            Frame con rostros detectados marcados o None
        """
        frame = self.camera_manager.get_frame()
        if frame is None:
            return None
        
        try:
            # Detectar rostros
            faces = self.face_detector.detect_faces(frame)
            
            # Dibujar rectángulos alrededor de rostros
            if faces:
                frame = self.face_detector.draw_face_rectangles(frame, faces)
                
                # Agregar información adicional si hay reconocimiento
                if self.face_recognizer.is_ready():
                    for i, (x, y, w, h) in enumerate(faces):
                        # Extraer región del rostro
                        face_region = frame[y:y+h, x:x+w]
                        
                        # Intentar reconocimiento
                        recognition_result = self.face_recognizer.recognize_face(face_region)
                        
                        if recognition_result['success']:
                            # Dibujar nombre y confianza
                            text = f"{recognition_result['student_name']} ({recognition_result['confidence']:.1f}%)"
                            cv2.putText(frame, text, (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            # Dibujar "Desconocido"
                            cv2.putText(frame, "Desconocido", (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Agregar información del sistema
            self._add_system_info_to_frame(frame)
            
            return frame
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Error procesando frame: {str(e)}")
            return frame
    
    def capture_and_register_student(self, student_id: str, num_samples: int = 5) -> Dict[str, Any]:
        """
        Capturar y registrar muestras de un estudiante
        
        Args:
            student_id: ID del estudiante
            num_samples: Número de muestras a capturar
            
        Returns:
            Resultado de la operación
        """
        try:
            from models.student_model import student_model
            
            # Verificar que el estudiante existe
            student = student_model.get_student_by_id(student_id)
            if not student:
                return {
                    'success': False,
                    'message': 'Estudiante no encontrado'
                }
            
            captured_faces = []
            capture_count = 0
            
            print(f"Capturando {num_samples} muestras para {student['full_name']}...")
            
            # Capturar muestras
            for i in range(num_samples * 3):  # Intentos adicionales por si falla alguno
                if capture_count >= num_samples:
                    break
                
                # Obtener frame
                frame = self.camera_manager.capture_single_frame()
                if frame is None:
                    continue
                
                # Detectar y extraer mejor rostro
                best_face = self.face_detector.detect_and_extract_best_face(frame)
                if best_face is not None:
                    # Validar calidad
                    quality = self.face_detector.validate_face_quality(best_face)
                    
                    if quality['valid']:
                        captured_faces.append(best_face)
                        capture_count += 1
                        print(f"Muestra {capture_count}/{num_samples} capturada")
                        
                        # Pausa entre capturas
                        time.sleep(0.5)
                    else:
                        print(f"Muestra descartada: {', '.join(quality['errors'])}")
                
                time.sleep(0.1)
            
            if len(captured_faces) == 0:
                return {
                    'success': False,
                    'message': 'No se pudo capturar ninguna muestra válida'
                }
            
            # Guardar muestras usando el reconocedor
            save_result = self.face_recognizer.add_training_samples(student_id, captured_faces)
            
            if save_result['success']:
                # Actualizar modelo si es necesario
                if self.face_recognizer.is_ready():
                    update_result = self.face_recognizer.update_model_with_new_student(student_id)
                    if not update_result['success']:
                        print(f"Advertencia: {update_result['message']}")
                
                return {
                    'success': True,
                    'message': f'Se capturaron {len(captured_faces)} muestras para {student["full_name"]}',
                    'samples_captured': len(captured_faces)
                }
            else:
                return save_result
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error capturando muestras: {str(e)}'
            }
    
    def train_model(self) -> Dict[str, Any]:
        """
        Entrenar el modelo de reconocimiento
        
        Returns:
            Resultado del entrenamiento
        """
        return self.face_recognizer.train_model(force_retrain=True)
    
    def record_manual_attendance(self, student_id: str) -> Dict[str, Any]:
        """
        Registrar asistencia manualmente
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Resultado del registro
        """
        try:
            from models.attendance_model import attendance_model
            
            result = attendance_model.record_attendance(
                student_id=student_id,
                confidence=100.0,
                method="manual"
            )
            
            if result['success']:
                self.stats['attendance_recorded'] += 1
                if self.on_attendance_recorded:
                    self.on_attendance_recorded(result['attendance'])
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error registrando asistencia: {str(e)}'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtener estado del sistema
        
        Returns:
            Diccionario con estado completo del sistema
        """
        status = {
            'running': self.is_running,
            'camera': self.camera_manager.get_camera_info(),
            'detector': self.face_detector.get_detection_statistics(),
            'recognizer': self.face_recognizer.get_model_info(),
            'statistics': self.stats.copy(),
            'configuration': {
                'recognition_interval': self.recognition_interval,
                'auto_attendance': self.auto_attendance,
                'cache_timeout': self.cache_timeout
            }
        }
        
        # Calcular tiempo de funcionamiento
        if self.stats['start_time']:
            uptime = datetime.now() - self.stats['start_time']
            status['uptime_seconds'] = uptime.total_seconds()
        
        return status
    
    def set_callbacks(self, **callbacks):
        """
        Establecer callbacks para eventos del sistema
        
        Args:
            on_face_detected: Callback cuando se detecta un rostro
            on_face_recognized: Callback cuando se reconoce un rostro
            on_attendance_recorded: Callback cuando se registra asistencia
            on_error: Callback para errores
        """
        self.on_face_detected = callbacks.get('on_face_detected')
        self.on_face_recognized = callbacks.get('on_face_recognized')
        self.on_attendance_recorded = callbacks.get('on_attendance_recorded')
        self.on_error = callbacks.get('on_error')
    
    def set_configuration(self, **config_updates):
        """
        Actualizar configuración del sistema
        
        Args:
            recognition_interval: Intervalo entre reconocimientos
            auto_attendance: Activar registro automático
            cache_timeout: Tiempo de cache de reconocimientos
        """
        if 'recognition_interval' in config_updates:
            self.recognition_interval = max(0.1, config_updates['recognition_interval'])
        
        if 'auto_attendance' in config_updates:
            self.auto_attendance = bool(config_updates['auto_attendance'])
        
        if 'cache_timeout' in config_updates:
            self.cache_timeout = max(1.0, config_updates['cache_timeout'])
    
    def _recognition_loop(self):
        """Bucle principal de reconocimiento (ejecutado en hilo separado)"""
        print("Bucle de reconocimiento iniciado")
        
        while self.is_running:
            try:
                # Obtener frame actual
                frame = self.camera_manager.get_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detectar rostros
                faces = self.face_detector.detect_faces(frame)
                
                if faces:
                    self.stats['faces_detected'] += len(faces)
                    
                    # Notificar detección
                    if self.on_face_detected:
                        self.on_face_detected(faces)
                    
                    # Procesar reconocimiento si el modelo está listo
                    if self.face_recognizer.is_ready():
                        self._process_face_recognition(frame, faces)
                
                # Limpiar cache expirado
                self._cleanup_recognition_cache()
                
                # Esperar intervalo configurado
                time.sleep(self.recognition_interval)
                
            except Exception as e:
                self.stats['errors'] += 1
                if self.on_error:
                    self.on_error(f"Error en bucle de reconocimiento: {str(e)}")
                time.sleep(1.0)
        
        print("Bucle de reconocimiento terminado")
    
    def _process_face_recognition(self, frame: np.ndarray, faces: List):
        """Procesar reconocimiento de rostros detectados"""
        for (x, y, w, h) in faces:
            try:
                # Extraer región del rostro
                face_region = frame[y:y+h, x:x+w]
                
                # Realizar reconocimiento
                recognition_result = self.face_recognizer.recognize_face(face_region)
                
                if recognition_result['success']:
                    self.stats['faces_recognized'] += 1
                    self.stats['last_recognition'] = datetime.now()
                    
                    student_id = recognition_result['student_id']
                    
                    # Verificar cache para evitar duplicados
                    if not self._is_in_recognition_cache(student_id):
                        # Agregar a cache
                        self._add_to_recognition_cache(student_id)
                        
                        # Notificar reconocimiento
                        if self.on_face_recognized:
                            self.on_face_recognized(recognition_result)
                        
                        # Registrar asistencia automáticamente si está habilitado
                        if self.auto_attendance:
                            self._auto_record_attendance(recognition_result)
                
            except Exception as e:
                self.stats['errors'] += 1
                if self.on_error:
                    self.on_error(f"Error procesando reconocimiento: {str(e)}")
    
    def _auto_record_attendance(self, recognition_result: Dict):
        """Registrar asistencia automáticamente"""
        try:
            from models.attendance_model import attendance_model
            
            attendance_result = attendance_model.record_attendance(
                student_id=recognition_result['student_id'],
                confidence=recognition_result['confidence'],
                method="facial_recognition"
            )
            
            if attendance_result['success']:
                self.stats['attendance_recorded'] += 1
                if self.on_attendance_recorded:
                    self.on_attendance_recorded(attendance_result['attendance'])
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Error registrando asistencia automática: {str(e)}")
    
    def _is_in_recognition_cache(self, student_id: str) -> bool:
        """Verificar si un estudiante está en el cache de reconocimiento"""
        if student_id in self.recognition_cache:
            time_diff = time.time() - self.recognition_cache[student_id]
            return time_diff < self.cache_timeout
        return False
    
    def _add_to_recognition_cache(self, student_id: str):
        """Agregar estudiante al cache de reconocimiento"""
        self.recognition_cache[student_id] = time.time()
    
    def _cleanup_recognition_cache(self):
        """Limpiar entradas expiradas del cache"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.recognition_cache.items()
            if current_time - timestamp > self.cache_timeout
        ]
        
        for key in expired_keys:
            del self.recognition_cache[key]
    
    def _add_system_info_to_frame(self, frame: np.ndarray):
        """Agregar información del sistema al frame"""
        try:
            height, width = frame.shape[:2]
            
            # Información básica
            info_lines = [
                f"Estado: {'Activo' if self.is_running else 'Inactivo'}",
                f"Rostros detectados: {self.stats['faces_detected']}",
                f"Rostros reconocidos: {self.stats['faces_recognized']}",
                f"Asistencias: {self.stats['attendance_recorded']}"
            ]
            
            # Dibujar información
            y_offset = 30
            for line in info_lines:
                cv2.putText(frame, line, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 20
            
            # FPS de la cámara
            fps_text = f"FPS: {self.camera_manager.fps:.1f}"
            cv2.putText(frame, fps_text, (width - 100, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        except Exception as e:
            pass  # Ignorar errores de visualización
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        self.stop_recognition()

# Crear instancia global del sistema
recognition_system = FaceRecognitionSystem()
