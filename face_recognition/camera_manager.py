#!/usr/bin/env python3
"""
AsistoYA - Gestor de Cámara
Manejo de captura de video y configuraciones de cámara
"""

import cv2
import numpy as np
import threading
import time
from typing import Optional, Tuple, Dict, Any
import config

class CameraManager:
    """Gestor de cámara para captura de video"""
    
    def __init__(self, camera_index: int = None):
        """
        Inicializar el gestor de cámara
        
        Args:
            camera_index: Índice de la cámara (None para usar configuración por defecto)
        """
        self.camera_index = camera_index if camera_index is not None else config.DEFAULT_CAMERA_INDEX
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
        # Configuraciones de video
        self.frame_width = config.FRAME_WIDTH
        self.frame_height = config.FRAME_HEIGHT
        
        # Estadísticas
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0
        
        # Estado de la cámara
        self.camera_available = False
        self.error_message = ""
    
    def initialize_camera(self) -> bool:
        """
        Inicializar la conexión con la cámara
        
        Returns:
            True si la cámara se inicializó correctamente
        """
        try:
            # Liberar cámara anterior si existe
            if self.cap is not None:
                self.cap.release()
            
            # Crear nueva captura
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.error_message = f"No se pudo abrir la cámara con índice {self.camera_index}"
                self.camera_available = False
                return False
            
            # Configurar propiedades de la cámara
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Verificar que la cámara funciona capturando un frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.error_message = "La cámara no pudo capturar frames"
                self.camera_available = False
                return False
            
            self.camera_available = True
            self.error_message = ""
            
            print(f"Cámara inicializada exitosamente: {self.camera_index}")
            print(f"Resolución: {self.get_actual_resolution()}")
            
            return True
            
        except Exception as e:
            self.error_message = f"Error inicializando cámara: {str(e)}"
            self.camera_available = False
            print(self.error_message)
            return False
    
    def start_capture(self) -> bool:
        """
        Iniciar captura continua en hilo separado
        
        Returns:
            True si se inició correctamente
        """
        if not self.camera_available:
            if not self.initialize_camera():
                return False
        
        if self.is_running:
            return True
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        return True
    
    def stop_capture(self):
        """Detener captura continua"""
        self.is_running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.camera_available = False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Obtener el frame actual
        
        Returns:
            Frame actual o None si no está disponible
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def capture_single_frame(self) -> Optional[np.ndarray]:
        """
        Capturar un frame único (sin usar captura continua)
        
        Returns:
            Frame capturado o None si hay error
        """
        if not self.camera_available:
            if not self.initialize_camera():
                return None
        
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                return frame
            else:
                self.error_message = "No se pudo capturar frame"
                return None
                
        except Exception as e:
            self.error_message = f"Error capturando frame: {str(e)}"
            return None
    
    def get_camera_info(self) -> Dict[str, Any]:
        """
        Obtener información de la cámara
        
        Returns:
            Diccionario con información de la cámara
        """
        info = {
            'camera_index': self.camera_index,
            'available': self.camera_available,
            'is_running': self.is_running,
            'error_message': self.error_message,
            'fps': self.fps,
            'frame_count': self.frame_count
        }
        
        if self.camera_available and self.cap:
            try:
                info.update({
                    'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'actual_fps': self.cap.get(cv2.CAP_PROP_FPS),
                    'backend': self.cap.getBackendName() if hasattr(self.cap, 'getBackendName') else 'Unknown'
                })
            except Exception as e:
                info['properties_error'] = str(e)
        
        return info
    
    def get_actual_resolution(self) -> Tuple[int, int]:
        """
        Obtener resolución actual de la cámara
        
        Returns:
            Tupla (width, height)
        """
        if self.cap and self.camera_available:
            try:
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                return (width, height)
            except:
                pass
        
        return (self.frame_width, self.frame_height)
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Cambiar resolución de la cámara
        
        Args:
            width: Ancho en píxeles
            height: Alto en píxeles
            
        Returns:
            True si se cambió exitosamente
        """
        if not self.camera_available:
            return False
        
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Verificar cambio
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.frame_width = actual_width
            self.frame_height = actual_height
            
            return True
            
        except Exception as e:
            self.error_message = f"Error cambiando resolución: {str(e)}"
            return False
    
    def auto_adjust_exposure(self) -> bool:
        """
        Ajustar automáticamente la exposición
        
        Returns:
            True si se ajustó exitosamente
        """
        if not self.camera_available:
            return False
        
        try:
            # Habilitar auto-exposición
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
            return True
        except Exception as e:
            self.error_message = f"Error ajustando exposición: {str(e)}"
            return False
    
    def take_photo(self, filename: str = None) -> Optional[str]:
        """
        Tomar una foto y guardarla
        
        Args:
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado o None si hay error
        """
        frame = self.get_frame() if self.is_running else self.capture_single_frame()
        
        if frame is None:
            return None
        
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}.jpg"
            
            # Asegurar que el archivo tenga extensión
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filename += '.jpg'
            
            # Guardar imagen
            success = cv2.imwrite(filename, frame)
            
            if success:
                return filename
            else:
                self.error_message = "Error guardando foto"
                return None
                
        except Exception as e:
            self.error_message = f"Error tomando foto: {str(e)}"
            return None
    
    def get_available_cameras(self) -> list:
        """
        Detectar cámaras disponibles en el sistema
        
        Returns:
            Lista de índices de cámaras disponibles
        """
        available_cameras = []
        
        # Probar índices del 0 al 10
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(i)
                cap.release()
            except:
                continue
        
        return available_cameras
    
    def switch_camera(self, new_index: int) -> bool:
        """
        Cambiar a una cámara diferente
        
        Args:
            new_index: Nuevo índice de cámara
            
        Returns:
            True si se cambió exitosamente
        """
        # Detener captura actual
        was_running = self.is_running
        if was_running:
            self.stop_capture()
        
        # Cambiar índice y reinicializar
        self.camera_index = new_index
        
        if self.initialize_camera():
            if was_running:
                return self.start_capture()
            return True
        
        return False
    
    def _capture_loop(self):
        """Bucle principal de captura (ejecutado en hilo separado)"""
        consecutive_errors = 0
        max_errors = 5
        
        while self.is_running:
            try:
                if not self.cap or not self.cap.isOpened():
                    if not self.initialize_camera():
                        time.sleep(1)
                        continue
                
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame
                    
                    # Actualizar estadísticas
                    self.frame_count += 1
                    self._update_fps()
                    
                    consecutive_errors = 0
                    
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= max_errors:
                        self.error_message = "Muchos errores consecutivos en captura"
                        self.camera_available = False
                        break
                
                # Control de velocidad
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                consecutive_errors += 1
                self.error_message = f"Error en bucle de captura: {str(e)}"
                
                if consecutive_errors >= max_errors:
                    self.camera_available = False
                    break
                
                time.sleep(0.1)
        
        # Limpiar al salir
        if self.cap:
            self.cap.release()
        
        self.is_running = False
    
    def _update_fps(self):
        """Actualizar cálculo de FPS"""
        current_time = time.time()
        
        if hasattr(self, '_fps_frame_count'):
            self._fps_frame_count += 1
        else:
            self._fps_frame_count = 1
            self._fps_start_time = current_time
        
        # Calcular FPS cada segundo
        if current_time - self._fps_start_time >= 1.0:
            self.fps = self._fps_frame_count / (current_time - self._fps_start_time)
            self._fps_frame_count = 0
            self._fps_start_time = current_time
    
    def __del__(self):
        """Destructor para limpiar recursos"""
        self.stop_capture()

# Función de utilidad para probar cámaras
def test_camera(camera_index: int = 0) -> Dict[str, Any]:
    """
    Probar una cámara específica
    
    Args:
        camera_index: Índice de la cámara a probar
        
    Returns:
        Diccionario con resultados de la prueba
    """
    manager = CameraManager(camera_index)
    
    result = {
        'camera_index': camera_index,
        'available': False,
        'resolution': None,
        'can_capture': False,
        'error': None
    }
    
    try:
        if manager.initialize_camera():
            result['available'] = True
            result['resolution'] = manager.get_actual_resolution()
            
            # Probar captura
            frame = manager.capture_single_frame()
            if frame is not None:
                result['can_capture'] = True
                result['frame_shape'] = frame.shape
            else:
                result['error'] = manager.error_message
        else:
            result['error'] = manager.error_message
            
    except Exception as e:
        result['error'] = str(e)
    
    finally:
        manager.stop_capture()
    
    return result

def get_system_cameras() -> list:
    """
    Obtener información de todas las cámaras del sistema
    
    Returns:
        Lista con información de cámaras disponibles
    """
    cameras = []
    
    for i in range(5):  # Probar primeras 5 cámaras
        camera_info = test_camera(i)
        if camera_info['available']:
            cameras.append(camera_info)
    
    return cameras
