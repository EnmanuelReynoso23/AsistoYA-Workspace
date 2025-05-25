#!/usr/bin/env python3
"""
AsistoYA - Reconocedor de Rostros
Sistema de reconocimiento facial usando LBPH
"""

import cv2
import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional, Any
import config
from models.database import db_manager

class FaceRecognizer:
    """Reconocedor de rostros usando algoritmo LBPH (Local Binary Patterns Histograms)"""
    
    def __init__(self):
        """Inicializar el reconocedor de rostros"""
        self.recognizer = None
        self.names_dict = {}
        self.model_trained = False
        self.error_message = ""
        
        # Configuraciones
        self.confidence_threshold = config.DEFAULT_CONFIDENCE_THRESHOLD
        
        # Estadísticas
        self.recognition_count = 0
        self.last_recognition_time = None
        
        # Inicializar reconocedor
        self.initialize_recognizer()
        
        # Cargar modelo y nombres si existen
        self.load_model()
        self.load_names_dict()
    
    def initialize_recognizer(self) -> bool:
        """
        Inicializar el reconocedor LBPH
        
        Returns:
            True si se inicializó correctamente
        """
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create(
                radius=config.LBPH_RADIUS,
                neighbors=config.LBPH_NEIGHBORS,
                grid_x=config.LBPH_GRID_X,
                grid_y=config.LBPH_GRID_Y
            )
            
            print("Reconocedor LBPH inicializado correctamente")
            return True
            
        except Exception as e:
            self.error_message = f"Error inicializando reconocedor: {str(e)}"
            print(self.error_message)
            return False
    
    def train_model(self, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Entrenar el modelo con las imágenes disponibles
        
        Args:
            force_retrain: Forzar reentrenamiento aunque ya exista un modelo
            
        Returns:
            Resultado del entrenamiento
        """
        try:
            # Verificar si ya existe modelo y no se fuerza reentrenamiento
            if self.model_trained and not force_retrain:
                return {
                    'success': True,
                    'message': 'Modelo ya entrenado',
                    'faces_processed': 0
                }
            
            # Cargar imágenes y etiquetas
            faces, labels, names_mapping = self._load_training_data()
            
            if len(faces) == 0:
                return {
                    'success': False,
                    'message': 'No se encontraron imágenes para entrenar'
                }
            
            # Entrenar el modelo
            self.recognizer.train(faces, np.array(labels))
            
            # Guardar modelo
            model_saved = self.save_model()
            
            # Actualizar diccionario de nombres
            self.names_dict = names_mapping
            names_saved = self.save_names_dict()
            
            if model_saved and names_saved:
                self.model_trained = True
                return {
                    'success': True,
                    'message': f'Modelo entrenado exitosamente con {len(faces)} rostros',
                    'faces_processed': len(faces),
                    'unique_people': len(names_mapping)
                }
            else:
                return {
                    'success': False,
                    'message': 'Error guardando el modelo entrenado'
                }
                
        except Exception as e:
            self.error_message = f"Error entrenando modelo: {str(e)}"
            return {
                'success': False,
                'message': self.error_message
            }
    
    def recognize_face(self, face_image: np.ndarray) -> Dict[str, Any]:
        """
        Reconocer un rostro
        
        Args:
            face_image: Imagen del rostro a reconocer
            
        Returns:
            Resultado del reconocimiento
        """
        if not self.model_trained:
            return {
                'success': False,
                'message': 'Modelo no entrenado',
                'confidence': 0.0,
                'student_id': None,
                'student_name': None
            }
        
        try:
            # Preparar imagen
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image.copy()
            
            # Redimensionar al tamaño estándar
            gray = cv2.resize(gray, config.FACE_SIZE)
            
            # Realizar predicción
            label, confidence = self.recognizer.predict(gray)
            
            # Convertir confianza a porcentaje (menor valor = mayor confianza)
            confidence_percentage = max(0, 100 - confidence)
            
            # Actualizar estadísticas
            self.recognition_count += 1
            self.last_recognition_time = cv2.getTickCount()
            
            # Verificar si la confianza supera el umbral
            if confidence_percentage >= self.confidence_threshold:
                student_id = self.names_dict.get(str(label), 'unknown')
                
                # Obtener información del estudiante
                from models.student_model import student_model
                student = student_model.get_student_by_id(student_id)
                student_name = student['full_name'] if student else 'Desconocido'
                
                return {
                    'success': True,
                    'message': f'Rostro reconocido: {student_name}',
                    'confidence': round(confidence_percentage, 2),
                    'student_id': student_id,
                    'student_name': student_name,
                    'raw_confidence': confidence,
                    'label': label
                }
            else:
                return {
                    'success': False,
                    'message': f'Confianza insuficiente: {confidence_percentage:.2f}%',
                    'confidence': round(confidence_percentage, 2),
                    'student_id': None,
                    'student_name': None,
                    'raw_confidence': confidence,
                    'label': label
                }
                
        except Exception as e:
            self.error_message = f"Error reconociendo rostro: {str(e)}"
            return {
                'success': False,
                'message': self.error_message,
                'confidence': 0.0,
                'student_id': None,
                'student_name': None
            }
    
    def add_training_samples(self, student_id: str, face_images: List[np.ndarray]) -> Dict[str, Any]:
        """
        Agregar muestras de entrenamiento para un estudiante
        
        Args:
            student_id: ID del estudiante
            face_images: Lista de imágenes de rostros
            
        Returns:
            Resultado de la operación
        """
        try:
            if not face_images:
                return {
                    'success': False,
                    'message': 'No se proporcionaron imágenes'
                }
            
            # Verificar que el estudiante existe
            from models.student_model import student_model
            student = student_model.get_student_by_id(student_id)
            if not student:
                return {
                    'success': False,
                    'message': 'Estudiante no encontrado'
                }
            
            # Guardar imágenes en el directorio de rostros
            saved_count = 0
            
            for i, face_image in enumerate(face_images):
                try:
                    # Preparar imagen
                    if len(face_image.shape) == 3:
                        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face_image.copy()
                    
                    # Redimensionar
                    gray = cv2.resize(gray, config.FACE_SIZE)
                    
                    # Generar nombre de archivo
                    timestamp = cv2.getTickCount()
                    filename = f"{student['full_name']}_{student_id}_{timestamp}_{i}.jpg"
                    # Limpiar caracteres especiales
                    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
                    file_path = os.path.join(config.FACES_DIR, filename)
                    
                    # Guardar imagen
                    if cv2.imwrite(file_path, gray):
                        saved_count += 1
                    
                except Exception as e:
                    print(f"Error guardando imagen {i}: {e}")
                    continue
            
            if saved_count > 0:
                # Actualizar información del estudiante
                student_model.update_student(student_id, 
                                           face_registered=True,
                                           face_count=saved_count)
                
                return {
                    'success': True,
                    'message': f'Se guardaron {saved_count} imágenes de entrenamiento',
                    'saved_count': saved_count
                }
            else:
                return {
                    'success': False,
                    'message': 'No se pudo guardar ninguna imagen'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error agregando muestras: {str(e)}'
            }
    
    def update_model_with_new_student(self, student_id: str) -> Dict[str, Any]:
        """
        Actualizar modelo con un nuevo estudiante
        
        Args:
            student_id: ID del nuevo estudiante
            
        Returns:
            Resultado de la actualización
        """
        try:
            # Cargar imágenes del estudiante
            student_faces, student_labels = self._load_student_images(student_id)
            
            if len(student_faces) == 0:
                return {
                    'success': False,
                    'message': f'No se encontraron imágenes para el estudiante {student_id}'
                }
            
            if self.model_trained:
                # Actualizar modelo existente
                self.recognizer.update(student_faces, np.array(student_labels))
            else:
                # Si no hay modelo, entrenar desde cero
                return self.train_model()
            
            # Actualizar diccionario de nombres
            new_label = max(map(int, self.names_dict.keys())) + 1 if self.names_dict else 0
            self.names_dict[str(new_label)] = student_id
            
            # Guardar cambios
            model_saved = self.save_model()
            names_saved = self.save_names_dict()
            
            if model_saved and names_saved:
                return {
                    'success': True,
                    'message': f'Modelo actualizado con {len(student_faces)} nuevas muestras',
                    'samples_added': len(student_faces)
                }
            else:
                return {
                    'success': False,
                    'message': 'Error guardando modelo actualizado'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error actualizando modelo: {str(e)}'
            }
    
    def save_model(self) -> bool:
        """
        Guardar el modelo entrenado
        
        Returns:
            True si se guardó correctamente
        """
        try:
            if self.recognizer is None:
                return False
            
            os.makedirs(config.DATA_DIR, exist_ok=True)
            self.recognizer.save(config.FACE_MODEL_FILE)
            return True
            
        except Exception as e:
            self.error_message = f"Error guardando modelo: {str(e)}"
            return False
    
    def load_model(self) -> bool:
        """
        Cargar modelo previamente entrenado
        
        Returns:
            True si se cargó correctamente
        """
        try:
            if not os.path.exists(config.FACE_MODEL_FILE):
                return False
            
            if self.recognizer is None:
                self.initialize_recognizer()
            
            self.recognizer.read(config.FACE_MODEL_FILE)
            self.model_trained = True
            
            print("Modelo de reconocimiento facial cargado exitosamente")
            return True
            
        except Exception as e:
            self.error_message = f"Error cargando modelo: {str(e)}"
            return False
    
    def save_names_dict(self) -> bool:
        """
        Guardar diccionario de nombres
        
        Returns:
            True si se guardó correctamente
        """
        try:
            os.makedirs(config.DATA_DIR, exist_ok=True)
            
            with open(config.NAMES_DICT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.names_dict, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.error_message = f"Error guardando diccionario de nombres: {str(e)}"
            return False
    
    def load_names_dict(self) -> bool:
        """
        Cargar diccionario de nombres
        
        Returns:
            True si se cargó correctamente
        """
        try:
            if not os.path.exists(config.NAMES_DICT_FILE):
                self.names_dict = {}
                return True
            
            with open(config.NAMES_DICT_FILE, 'r', encoding='utf-8') as f:
                self.names_dict = json.load(f)
            
            return True
            
        except Exception as e:
            self.error_message = f"Error cargando diccionario de nombres: {str(e)}"
            self.names_dict = {}
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtener información del modelo
        
        Returns:
            Diccionario con información del modelo
        """
        info = {
            'model_trained': self.model_trained,
            'confidence_threshold': self.confidence_threshold,
            'recognition_count': self.recognition_count,
            'last_recognition_time': self.last_recognition_time,
            'error_message': self.error_message,
            'names_count': len(self.names_dict),
            'registered_students': list(self.names_dict.values())
        }
        
        # Información del archivo de modelo
        if os.path.exists(config.FACE_MODEL_FILE):
            stat = os.stat(config.FACE_MODEL_FILE)
            info['model_file_size'] = stat.st_size
            info['model_last_modified'] = stat.st_mtime
        
        return info
    
    def set_confidence_threshold(self, threshold: float) -> bool:
        """
        Establecer umbral de confianza
        
        Args:
            threshold: Nuevo umbral (0-100)
            
        Returns:
            True si se estableció correctamente
        """
        if 0 <= threshold <= 100:
            self.confidence_threshold = threshold
            return True
        return False
    
    def _load_training_data(self) -> Tuple[List[np.ndarray], List[int], Dict[str, str]]:
        """
        Cargar datos de entrenamiento desde el directorio de rostros
        
        Returns:
            Tupla con (faces, labels, names_mapping)
        """
        faces = []
        labels = []
        names_mapping = {}
        current_label = 0
        
        try:
            if not os.path.exists(config.FACES_DIR):
                return faces, labels, names_mapping
            
            # Obtener estudiantes registrados
            from models.student_model import student_model
            students = student_model.get_students_with_faces()
            
            for student in students:
                student_id = student['student_id']
                student_faces = []
                
                # Buscar archivos de imágenes del estudiante
                for filename in os.listdir(config.FACES_DIR):
                    if student_id in filename and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        file_path = os.path.join(config.FACES_DIR, filename)
                        
                        try:
                            # Cargar imagen
                            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                            if image is not None:
                                # Redimensionar al tamaño estándar
                                image = cv2.resize(image, config.FACE_SIZE)
                                student_faces.append(image)
                        except Exception as e:
                            print(f"Error cargando imagen {filename}: {e}")
                            continue
                
                # Agregar rostros del estudiante
                if student_faces:
                    for face in student_faces:
                        faces.append(face)
                        labels.append(current_label)
                    
                    names_mapping[str(current_label)] = student_id
                    current_label += 1
            
        except Exception as e:
            print(f"Error cargando datos de entrenamiento: {e}")
        
        return faces, labels, names_mapping
    
    def _load_student_images(self, student_id: str) -> Tuple[List[np.ndarray], List[int]]:
        """
        Cargar imágenes de un estudiante específico
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Tupla con (faces, labels)
        """
        faces = []
        labels = []
        
        try:
            if not os.path.exists(config.FACES_DIR):
                return faces, labels
            
            # Determinar etiqueta para el estudiante
            if student_id in self.names_dict.values():
                # Encontrar etiqueta existente
                label = next(int(k) for k, v in self.names_dict.items() if v == student_id)
            else:
                # Crear nueva etiqueta
                label = max(map(int, self.names_dict.keys())) + 1 if self.names_dict else 0
            
            # Cargar imágenes del estudiante
            for filename in os.listdir(config.FACES_DIR):
                if student_id in filename and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(config.FACES_DIR, filename)
                    
                    try:
                        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                        if image is not None:
                            image = cv2.resize(image, config.FACE_SIZE)
                            faces.append(image)
                            labels.append(label)
                    except Exception as e:
                        print(f"Error cargando imagen {filename}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error cargando imágenes del estudiante: {e}")
        
        return faces, labels
    
    def delete_student_from_model(self, student_id: str) -> Dict[str, Any]:
        """
        Eliminar estudiante del modelo (requiere reentrenamiento)
        
        Args:
            student_id: ID del estudiante a eliminar
            
        Returns:
            Resultado de la operación
        """
        try:
            # Eliminar archivos de imágenes
            if os.path.exists(config.FACES_DIR):
                deleted_files = 0
                for filename in os.listdir(config.FACES_DIR):
                    if student_id in filename:
                        file_path = os.path.join(config.FACES_DIR, filename)
                        try:
                            os.remove(file_path)
                            deleted_files += 1
                        except Exception as e:
                            print(f"Error eliminando archivo {filename}: {e}")
            
            # Reentrenar modelo
            retrain_result = self.train_model(force_retrain=True)
            
            if retrain_result['success']:
                return {
                    'success': True,
                    'message': f'Estudiante eliminado del modelo. Archivos eliminados: {deleted_files}',
                    'files_deleted': deleted_files
                }
            else:
                return {
                    'success': False,
                    'message': f'Error reentrenando modelo: {retrain_result["message"]}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error eliminando estudiante: {str(e)}'
            }
    
    def is_ready(self) -> bool:
        """
        Verificar si el reconocedor está listo
        
        Returns:
            True si está listo para reconocimiento
        """
        return self.recognizer is not None and self.model_trained

# Crear instancia global del reconocedor
face_recognizer = FaceRecognizer()
