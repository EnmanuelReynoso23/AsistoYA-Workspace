#!/usr/bin/env python3
"""
AsistoYA - Detector de Rostros
Sistema de detección de rostros usando OpenCV
"""

import cv2
import numpy as np
import os
from typing import List, Tuple, Optional, Dict, Any
import config

class FaceDetector:
    """Detector de rostros usando clasificadores Haar Cascade"""
    
    def __init__(self):
        """Inicializar el detector de rostros"""
        self.face_cascade = None
        self.detector_loaded = False
        self.error_message = ""
        
        # Configuraciones de detección
        self.scale_factor = config.DETECTION_SCALE_FACTOR
        self.min_neighbors = config.DETECTION_MIN_NEIGHBORS
        self.min_size = config.DETECTION_MIN_SIZE
        self.face_size = config.FACE_SIZE
        
        # Estadísticas
        self.detections_count = 0
        self.last_detection_time = None
        
        # Cargar detector
        self.load_detector()
    
    def load_detector(self) -> bool:
        """
        Cargar el clasificador Haar Cascade
        
        Returns:
            True si se cargó correctamente
        """
        try:
            # Buscar archivo de clasificador
            cascade_paths = [
                # Ruta absoluta de OpenCV
                cv2.data.haarcascades + config.HAAR_CASCADE_FILE,
                # Rutas relativas posibles
                config.HAAR_CASCADE_FILE,
                os.path.join('data', config.HAAR_CASCADE_FILE),
                os.path.join('face_recognition', config.HAAR_CASCADE_FILE),
                # Ruta completa por defecto
                'haarcascade_frontalface_default.xml'
            ]
            
            for cascade_path in cascade_paths:
                if os.path.exists(cascade_path):
                    self.face_cascade = cv2.CascadeClassifier(cascade_path)
                    
                    if not self.face_cascade.empty():
                        self.detector_loaded = True
                        self.error_message = ""
                        print(f"Detector de rostros cargado desde: {cascade_path}")
                        return True
            
            # Si no se encuentra, intentar cargar desde OpenCV directamente
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            if not self.face_cascade.empty():
                self.detector_loaded = True
                self.error_message = ""
                print("Detector de rostros cargado desde OpenCV")
                return True
            else:
                self.error_message = "No se pudo cargar el clasificador Haar Cascade"
                return False
                
        except Exception as e:
            self.error_message = f"Error cargando detector: {str(e)}"
            self.detector_loaded = False
            return False
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detectar rostros en un frame
        
        Args:
            frame: Frame de imagen en formato numpy array
            
        Returns:
            Lista de tuplas (x, y, width, height) con las ubicaciones de rostros
        """
        if not self.detector_loaded:
            return []
        
        try:
            # Convertir a escala de grises si es necesario
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Detectar rostros
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Actualizar estadísticas
            if len(faces) > 0:
                self.detections_count += len(faces)
                self.last_detection_time = cv2.getTickCount()
            
            return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
            
        except Exception as e:
            self.error_message = f"Error detectando rostros: {str(e)}"
            return []
    
    def extract_face_regions(self, frame: np.ndarray, 
                           faces: List[Tuple[int, int, int, int]] = None) -> List[np.ndarray]:
        """
        Extraer regiones de rostros del frame
        
        Args:
            frame: Frame de imagen
            faces: Lista de rostros detectados (si no se proporciona, se detectan automáticamente)
            
        Returns:
            Lista de imágenes de rostros extraídas
        """
        if faces is None:
            faces = self.detect_faces(frame)
        
        face_regions = []
        
        try:
            for (x, y, w, h) in faces:
                # Extraer región del rostro
                face_region = frame[y:y+h, x:x+w]
                
                if face_region.size > 0:
                    # Redimensionar al tamaño estándar
                    face_resized = cv2.resize(face_region, self.face_size)
                    face_regions.append(face_resized)
            
        except Exception as e:
            self.error_message = f"Error extrayendo rostros: {str(e)}"
        
        return face_regions
    
    def draw_face_rectangles(self, frame: np.ndarray, 
                           faces: List[Tuple[int, int, int, int]] = None,
                           color: Tuple[int, int, int] = (0, 255, 0),
                           thickness: int = 2) -> np.ndarray:
        """
        Dibujar rectángulos alrededor de rostros detectados
        
        Args:
            frame: Frame de imagen
            faces: Lista de rostros detectados (si no se proporciona, se detectan automáticamente)
            color: Color del rectángulo en formato BGR
            thickness: Grosor de las líneas
            
        Returns:
            Frame con rectángulos dibujados
        """
        if faces is None:
            faces = self.detect_faces(frame)
        
        frame_with_rectangles = frame.copy()
        
        try:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_with_rectangles, (x, y), (x+w, y+h), color, thickness)
                
                # Agregar texto con información
                cv2.putText(frame_with_rectangles, f"Face {w}x{h}", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
        except Exception as e:
            self.error_message = f"Error dibujando rectángulos: {str(e)}"
        
        return frame_with_rectangles
    
    def get_largest_face(self, faces: List[Tuple[int, int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
        """
        Obtener el rostro más grande de una lista
        
        Args:
            faces: Lista de rostros detectados
            
        Returns:
            Tupla con el rostro más grande o None si no hay rostros
        """
        if not faces:
            return None
        
        # Calcular área de cada rostro y encontrar el mayor
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return largest_face
    
    def filter_faces_by_size(self, faces: List[Tuple[int, int, int, int]],
                           min_area: int = 1000) -> List[Tuple[int, int, int, int]]:
        """
        Filtrar rostros por tamaño mínimo
        
        Args:
            faces: Lista de rostros detectados
            min_area: Área mínima en píxeles
            
        Returns:
            Lista de rostros filtrados
        """
        filtered_faces = []
        
        for (x, y, w, h) in faces:
            area = w * h
            if area >= min_area:
                filtered_faces.append((x, y, w, h))
        
        return filtered_faces
    
    def enhance_face_region(self, face_region: np.ndarray) -> np.ndarray:
        """
        Mejorar la calidad de una región de rostro
        
        Args:
            face_region: Imagen del rostro
            
        Returns:
            Imagen mejorada
        """
        try:
            # Convertir a escala de grises si es necesario
            if len(face_region.shape) == 3:
                gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_region.copy()
            
            # Aplicar ecualización de histograma
            enhanced = cv2.equalizeHist(gray)
            
            # Aplicar filtro de reducción de ruido
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            return enhanced
            
        except Exception as e:
            self.error_message = f"Error mejorando rostro: {str(e)}"
            return face_region
    
    def detect_and_extract_best_face(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detectar y extraer el mejor rostro del frame
        
        Args:
            frame: Frame de imagen
            
        Returns:
            Imagen del mejor rostro detectado o None
        """
        try:
            # Detectar rostros
            faces = self.detect_faces(frame)
            
            if not faces:
                return None
            
            # Filtrar por tamaño mínimo
            faces = self.filter_faces_by_size(faces, min_area=2500)  # 50x50 mínimo
            
            if not faces:
                return None
            
            # Obtener el rostro más grande
            best_face = self.get_largest_face(faces)
            
            if best_face:
                x, y, w, h = best_face
                face_region = frame[y:y+h, x:x+w]
                
                # Redimensionar al tamaño estándar
                face_resized = cv2.resize(face_region, self.face_size)
                
                # Mejorar calidad
                face_enhanced = self.enhance_face_region(face_resized)
                
                return face_enhanced
            
            return None
            
        except Exception as e:
            self.error_message = f"Error extrayendo mejor rostro: {str(e)}"
            return None
    
    def validate_face_quality(self, face_region: np.ndarray) -> Dict[str, Any]:
        """
        Validar la calidad de una imagen de rostro
        
        Args:
            face_region: Imagen del rostro
            
        Returns:
            Diccionario con métricas de calidad
        """
        quality = {
            'valid': False,
            'sharpness': 0.0,
            'brightness': 0.0,
            'contrast': 0.0,
            'size_ok': False,
            'errors': []
        }
        
        try:
            if face_region is None or face_region.size == 0:
                quality['errors'].append("Imagen vacía")
                return quality
            
            # Verificar tamaño
            h, w = face_region.shape[:2]
            quality['size_ok'] = w >= 50 and h >= 50
            
            if not quality['size_ok']:
                quality['errors'].append(f"Tamaño muy pequeño: {w}x{h}")
            
            # Convertir a escala de grises si es necesario
            if len(face_region.shape) == 3:
                gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_region.copy()
            
            # Calcular nitidez (usando varianza del Laplaciano)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            quality['sharpness'] = laplacian.var()
            
            # Calcular brillo promedio
            quality['brightness'] = np.mean(gray)
            
            # Calcular contraste (desviación estándar)
            quality['contrast'] = np.std(gray)
            
            # Criterios de calidad
            min_sharpness = 100.0
            min_brightness = 50.0
            max_brightness = 200.0
            min_contrast = 30.0
            
            # Validar criterios
            if quality['sharpness'] < min_sharpness:
                quality['errors'].append(f"Imagen borrosa (nitidez: {quality['sharpness']:.1f})")
            
            if quality['brightness'] < min_brightness:
                quality['errors'].append(f"Imagen muy oscura (brillo: {quality['brightness']:.1f})")
            elif quality['brightness'] > max_brightness:
                quality['errors'].append(f"Imagen muy clara (brillo: {quality['brightness']:.1f})")
            
            if quality['contrast'] < min_contrast:
                quality['errors'].append(f"Bajo contraste ({quality['contrast']:.1f})")
            
            # Determinar si es válida
            quality['valid'] = (
                quality['size_ok'] and
                quality['sharpness'] >= min_sharpness and
                min_brightness <= quality['brightness'] <= max_brightness and
                quality['contrast'] >= min_contrast
            )
            
        except Exception as e:
            quality['errors'].append(f"Error en validación: {str(e)}")
        
        return quality
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de detección
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'detector_loaded': self.detector_loaded,
            'total_detections': self.detections_count,
            'last_detection_time': self.last_detection_time,
            'error_message': self.error_message,
            'configuration': {
                'scale_factor': self.scale_factor,
                'min_neighbors': self.min_neighbors,
                'min_size': self.min_size,
                'face_size': self.face_size
            }
        }
    
    def update_detection_parameters(self, scale_factor: float = None,
                                  min_neighbors: int = None,
                                  min_size: Tuple[int, int] = None) -> bool:
        """
        Actualizar parámetros de detección
        
        Args:
            scale_factor: Factor de escala para detección
            min_neighbors: Número mínimo de vecinos
            min_size: Tamaño mínimo de rostro
            
        Returns:
            True si se actualizaron correctamente
        """
        try:
            if scale_factor is not None:
                if 1.1 <= scale_factor <= 2.0:
                    self.scale_factor = scale_factor
                else:
                    return False
            
            if min_neighbors is not None:
                if 1 <= min_neighbors <= 10:
                    self.min_neighbors = min_neighbors
                else:
                    return False
            
            if min_size is not None:
                if len(min_size) == 2 and min_size[0] > 0 and min_size[1] > 0:
                    self.min_size = min_size
                else:
                    return False
            
            return True
            
        except Exception as e:
            self.error_message = f"Error actualizando parámetros: {str(e)}"
            return False
    
    def is_ready(self) -> bool:
        """
        Verificar si el detector está listo para usar
        
        Returns:
            True si está listo
        """
        return self.detector_loaded and self.face_cascade is not None

# Función de utilidad para probar detección
def test_face_detection(image_path: str = None) -> Dict[str, Any]:
    """
    Probar detección de rostros con una imagen
    
    Args:
        image_path: Ruta de imagen para probar (None para usar cámara)
        
    Returns:
        Diccionario con resultados de la prueba
    """
    detector = FaceDetector()
    
    result = {
        'detector_ready': detector.is_ready(),
        'faces_detected': 0,
        'processing_time': 0,
        'error': None
    }
    
    if not detector.is_ready():
        result['error'] = detector.error_message
        return result
    
    try:
        if image_path and os.path.exists(image_path):
            # Cargar imagen desde archivo
            frame = cv2.imread(image_path)
        else:
            # Usar cámara
            from .camera_manager import CameraManager
            camera = CameraManager()
            if camera.initialize_camera():
                frame = camera.capture_single_frame()
                camera.stop_capture()
            else:
                result['error'] = "No se pudo acceder a la cámara"
                return result
        
        if frame is None:
            result['error'] = "No se pudo obtener imagen"
            return result
        
        # Medir tiempo de procesamiento
        start_time = cv2.getTickCount()
        
        # Detectar rostros
        faces = detector.detect_faces(frame)
        
        end_time = cv2.getTickCount()
        result['processing_time'] = (end_time - start_time) / cv2.getTickFrequency()
        result['faces_detected'] = len(faces)
        
        # Información adicional
        if faces:
            result['face_locations'] = faces
            result['largest_face_area'] = max(w * h for x, y, w, h in faces)
        
    except Exception as e:
        result['error'] = str(e)
    
    return result
