#!/usr/bin/env python3
"""
AsistoYA - Sistema Principal de Asistencia con Reconocimiento Facial
Aplicación principal reconstruida y mejorada
"""

import cv2
import os
import numpy as np
import time
import random
import string
import json
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
from datetime import datetime, timedelta
import threading
from PIL import Image, ImageTk
import pandas as pd

class AsistoYASystem:
    """Sistema principal de AsistoYA mejorado"""
    
    def __init__(self):
        # Configuración inicial
        self.data_dir = "data"
        self.faces_dir = "faces"
        self.reports_dir = "reports"
        
        # Crear directorios necesarios
        for directory in [self.data_dir, self.faces_dir, self.reports_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Archivos de datos
        self.students_file = os.path.join(self.data_dir, "students.json")
        self.attendance_file = os.path.join(self.data_dir, "attendance.json")
        self.classrooms_file = os.path.join(self.data_dir, "classrooms.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        # Cargar modelos de reconocimiento facial
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Datos del sistema
        self.students = self.load_students()
        self.attendance_records = self.load_attendance()
        self.classrooms = self.load_classrooms()
        self.settings = self.load_settings()
        
        # Variables de cámara
        self.camera = None
        self.camera_running = False
        
        # Datos de entrenamiento
        self.faces_data = []
        self.labels_data = []
        self.names_dict = {}
        
        self.load_face_data()
        self.train_recognizer()
        
        print("✅ AsistoYA System inicializado correctamente")
    
    def load_students(self):
        """Cargar datos de estudiantes"""
        try:
            if os.path.exists(self.students_file):
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error cargando estudiantes: {e}")
            return {}
    
    def save_students(self):
        """Guardar datos de estudiantes"""
        try:
            with open(self.students_file, 'w', encoding='utf-8') as f:
                json.dump(self.students, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando estudiantes: {e}")
    
    def load_attendance(self):
        """Cargar registros de asistencia"""
        try:
            if os.path.exists(self.attendance_file):
                with open(self.attendance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error cargando asistencia: {e}")
            return []
    
    def save_attendance(self):
        """Guardar registros de asistencia"""
        try:
            with open(self.attendance_file, 'w', encoding='utf-8') as f:
                json.dump(self.attendance_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando asistencia: {e}")
    
    def load_classrooms(self):
        """Cargar datos de aulas"""
        try:
            if os.path.exists(self.classrooms_file):
                with open(self.classrooms_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "AULA_001": {
                    "name": "Aula Principal",
                    "capacity": 30,
                    "location": "Edificio A - Piso 1"
                }
            }
        except Exception as e:
            print(f"Error cargando aulas: {e}")
            return {}
    
    def save_classrooms(self):
        """Guardar datos de aulas"""
        try:
            with open(self.classrooms_file, 'w', encoding='utf-8') as f:
                json.dump(self.classrooms, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando aulas: {e}")
    
    def load_settings(self):
        """Cargar configuraciones"""
        default_settings = {
            "recognition_threshold": 75,
            "camera_index": 0,
            "auto_backup": True,
            "cooldown_seconds": 10,
            "face_image_size": [150, 150]
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return {**default_settings, **loaded}
            return default_settings
        except Exception as e:
            print(f"Error cargando configuraciones: {e}")
            return default_settings
    
    def save_settings(self):
        """Guardar configuraciones"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando configuraciones: {e}")
    
    def generate_student_id(self, name):
        """Generar ID único para estudiante"""
        parts = name.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[1][0].upper()
        else:
            initials = name[:2].upper()
        
        # Agregar número único
        student_id = initials + str(len(self.students) + 1).zfill(3)
        
        # Verificar unicidad
        while student_id in self.students:
            student_id = initials + str(random.randint(100, 999))
        
        return student_id
    
    def initialize_camera(self):
        """Inicializar cámara"""
        try:
            camera_index = self.settings.get("camera_index", 0)
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                # Probar otros índices
                for i in range(5):
                    self.camera = cv2.VideoCapture(i)
                    if self.camera.isOpened():
                        self.settings["camera_index"] = i
                        break
                else:
                    return False
            
            # Configurar cámara
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return True
            
        except Exception as e:
            print(f"Error inicializando cámara: {e}")
            return False
    
    def release_camera(self):
        """Liberar recursos de cámara"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
    
    def detect_faces(self, frame):
        """Detectar rostros en frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.3, 
            minNeighbors=5, 
            minSize=(50, 50)
        )
        return faces, gray
    
    def register_student(self, name, student_data=None):
        """Registrar nuevo estudiante"""
        if not name or len(name.strip()) < 2:
            return False, "Nombre inválido"
        
        name = name.strip()
        if name in [s.get("name") for s in self.students.values()]:
            return False, "Estudiante ya existe"
        
        if not self.initialize_camera():
            return False, "No se pudo acceder a la cámara"
        
        print(f"Registrando estudiante: {name}")
        print("Presione ESPACIO para capturar rostro, ESC para cancelar")
        
        captured_faces = []
        target_faces = 5  # Capturar múltiples rostros para mejor entrenamiento
        
        while len(captured_faces) < target_faces:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            faces, gray = self.detect_faces(frame)
            
            # Mostrar frame con detecciones
            display_frame = frame.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, f"Rostros: {len(captured_faces)}/{target_faces}", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.putText(display_frame, f"Registrando: {name}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(display_frame, "ESPACIO: Capturar | ESC: Cancelar", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Registro de Estudiante", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                self.release_camera()
                return False, "Registro cancelado"
            elif key == 32:  # ESPACIO
                if len(faces) == 1:
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Redimensionar y procesar rostro
                    face_size = tuple(self.settings.get("face_image_size", [150, 150]))
                    face_resized = cv2.resize(face_roi, face_size)
                    face_normalized = cv2.equalizeHist(face_resized)
                    
                    captured_faces.append(face_normalized)
                    print(f"Rostro {len(captured_faces)}/{target_faces} capturado")
                    
                    time.sleep(0.5)  # Pausa para evitar capturas duplicadas
                else:
                    print("Asegúrese de que solo un rostro sea visible")
        
        self.release_camera()
        
        # Generar ID y guardar datos
        student_id = self.generate_student_id(name)
        
        # Guardar imágenes de rostros
        face_files = []
        for i, face_data in enumerate(captured_faces):
            face_filename = f"{student_id}_{name.replace(' ', '_')}_{i}.jpg"
            face_path = os.path.join(self.faces_dir, face_filename)
            cv2.imwrite(face_path, face_data)
            face_files.append(face_filename)
        
        # Crear registro de estudiante
        student_record = {
            "student_id": student_id,
            "name": name,
            "face_files": face_files,
            "registration_date": datetime.now().isoformat(),
            "total_attendance": 0,
            "last_attendance": None,
            **(student_data or {})
        }
        
        self.students[student_id] = student_record
        self.save_students()
        
        # Actualizar datos de entrenamiento
        self.load_face_data()
        self.train_recognizer()
        
        return True, f"Estudiante {name} registrado con ID: {student_id}"
    
    def load_face_data(self):
        """Cargar datos de rostros para entrenamiento"""
        self.faces_data = []
        self.labels_data = []
        self.names_dict = {}
        
        label_id = 0
        
        for student_id, student_data in self.students.items():
            face_files = student_data.get("face_files", [])
            
            for face_file in face_files:
                face_path = os.path.join(self.faces_dir, face_file)
                
                if os.path.exists(face_path):
                    face_img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
                    if face_img is not None:
                        self.faces_data.append(face_img)
                        self.labels_data.append(label_id)
            
            if face_files:  # Solo agregar al diccionario si tiene rostros
                self.names_dict[label_id] = student_data["name"]
                label_id += 1
        
        print(f"Cargados {len(self.faces_data)} rostros de {len(self.names_dict)} estudiantes")
    
    def train_recognizer(self):
        """Entrenar reconocedor facial"""
        if len(self.faces_data) < 2:
            print("Necesita al menos 2 rostros para entrenar el reconocedor")
            return False
        
        try:
            self.face_recognizer.train(self.faces_data, np.array(self.labels_data))
            
            # Guardar modelo entrenado
            model_path = os.path.join(self.data_dir, "face_model.yml")
            self.face_recognizer.save(model_path)
            
            # Guardar diccionario de nombres
            names_path = os.path.join(self.data_dir, "names_dict.json")
            with open(names_path, 'w', encoding='utf-8') as f:
                json.dump(self.names_dict, f, ensure_ascii=False, indent=2)
            
            print("✅ Reconocedor entrenado exitosamente")
            return True
            
        except Exception as e:
            print(f"Error entrenando reconocedor: {e}")
            return False
    
    def load_trained_model(self):
        """Cargar modelo entrenado"""
        try:
            model_path = os.path.join(self.data_dir, "face_model.yml")
            names_path = os.path.join(self.data_dir, "names_dict.json")
            
            if os.path.exists(model_path) and os.path.exists(names_path):
                self.face_recognizer.read(model_path)
                
                with open(names_path, 'r', encoding='utf-8') as f:
                    # Convertir claves string a int
                    names_data = json.load(f)
                    self.names_dict = {int(k): v for k, v in names_data.items()}
                
                return True
            return False
            
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            return False
    
    def recognize_face(self, face_roi):
        """Reconocer rostro"""
        if not self.names_dict:
            return None, 0
        
        try:
            # Procesar rostro
            face_size = tuple(self.settings.get("face_image_size", [150, 150]))
            face_resized = cv2.resize(face_roi, face_size)
            face_normalized = cv2.equalizeHist(face_resized)
            
            # Predecir
            label, confidence = self.face_recognizer.predict(face_normalized)
            
            # Convertir confianza a porcentaje (menor es mejor en LBPH)
            confidence_percent = max(0, 100 - confidence)
            
            threshold = self.settings.get("recognition_threshold", 75)
            
            if confidence_percent >= threshold and label in self.names_dict:
                return self.names_dict[label], confidence_percent
            
            return None, confidence_percent
            
        except Exception as e:
            print(f"Error en reconocimiento: {e}")
            return None, 0
    
    def mark_attendance(self, student_name, classroom_id="AULA_001"):
        """Marcar asistencia de estudiante"""
        # Buscar estudiante por nombre
        student_id = None
        for sid, sdata in self.students.items():
            if sdata["name"] == student_name:
                student_id = sid
                break
        
        if not student_id:
            return False, "Estudiante no encontrado"
        
        # Verificar cooldown
        cooldown = self.settings.get("cooldown_seconds", 10)
        current_time = datetime.now()
        
        # Buscar último registro del estudiante
        for record in reversed(self.attendance_records):
            if (record["student_id"] == student_id and 
                record["classroom_id"] == classroom_id):
                last_time = datetime.fromisoformat(record["timestamp"])
                if (current_time - last_time).total_seconds() < cooldown:
                    return False, f"Debe esperar {cooldown} segundos entre registros"
                break
        
        # Crear registro de asistencia
        attendance_record = {
            "student_id": student_id,
            "student_name": student_name,
            "classroom_id": classroom_id,
            "timestamp": current_time.isoformat(),
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "status": "present"
        }
        
        self.attendance_records.append(attendance_record)
        self.save_attendance()
        
        # Actualizar estadísticas del estudiante
        self.students[student_id]["total_attendance"] += 1
        self.students[student_id]["last_attendance"] = current_time.strftime("%Y-%m-%d")
        self.save_students()
        
        return True, f"Asistencia marcada para {student_name}"
    
    def get_statistics(self):
        """Obtener estadísticas del sistema"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        stats = {
            "total_students": len(self.students),
            "today_attendance": len([r for r in self.attendance_records if r["date"] == today]),
            "total_attendance_records": len(self.attendance_records),
            "students_with_faces": len([s for s in self.students.values() if s.get("face_files")]),
            "trained_model": len(self.names_dict) > 0
        }
        
        return stats

# Aplicación GUI mejorada
class AsistoYAGUI:
    """Interfaz gráfica mejorada para AsistoYA"""
    
    def __init__(self):
        self.system = AsistoYASystem()
        self.root = tk.Tk()
        
        # Variables de estado - Definir ANTES de crear la interfaz
        self.recognition_active = False
        self.current_classroom = "AULA_001"  # Definir aquí para evitar el error
        
        # Configurar ventana y crear interfaz
        self.setup_main_window()
        self.create_interface()
    
    def setup_main_window(self):
        """Configurar ventana principal"""
        self.root.title("AsistoYA - Sistema de Asistencia Facial")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz principal"""
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.create_dashboard_tab()
        self.create_students_tab()
        self.create_recognition_tab()
        self.create_attendance_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """Crear pestaña de dashboard"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Título
        title_label = tk.Label(dashboard_frame, text="AsistoYA - Dashboard", 
                              font=("Arial", 24, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # Frame de estadísticas
        stats_frame = tk.Frame(dashboard_frame, bg="#f0f0f0")
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Obtener estadísticas
        stats = self.system.get_statistics()
        
        # Crear tarjetas de estadísticas
        self.create_stat_card(stats_frame, "👥 Estudiantes", stats["total_students"], "#4CAF50")
        self.create_stat_card(stats_frame, "📅 Asistencia Hoy", stats["today_attendance"], "#2196F3")
        self.create_stat_card(stats_frame, "📊 Total Registros", stats["total_attendance_records"], "#FF9800")
        self.create_stat_card(stats_frame, "🎯 Rostros Entrenados", stats["students_with_faces"], "#9C27B0")
        
        # Botones de acción rápida
        actions_frame = tk.LabelFrame(dashboard_frame, text="Acciones Rápidas", 
                                    font=("Arial", 12, "bold"), bg="#f0f0f0")
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        buttons_frame = tk.Frame(actions_frame, bg="#f0f0f0")
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="🚀 Iniciar Reconocimiento", 
                 command=self.start_recognition, bg="#4CAF50", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="👤 Registrar Estudiante", 
                 command=self.quick_register_student, bg="#2196F3", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="📋 Exportar Reporte", 
                 command=self.export_report, bg="#FF9800", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Status del sistema
        self.status_label = tk.Label(dashboard_frame, text="✅ Sistema listo", 
                                   font=("Arial", 12), bg="#f0f0f0", fg="green")
        self.status_label.pack(pady=10)
    
    def create_stat_card(self, parent, title, value, color):
        """Crear tarjeta de estadística"""
        card_frame = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        title_label = tk.Label(card_frame, text=title, font=("Arial", 12, "bold"), 
                              bg=color, fg="white")
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(card_frame, text=str(value), font=("Arial", 20, "bold"), 
                              bg=color, fg="white")
        value_label.pack(pady=(0, 10))
    
    def create_students_tab(self):
        """Crear pestaña de estudiantes"""
        students_frame = ttk.Frame(self.notebook)
        self.notebook.add(students_frame, text="👥 Estudiantes")
        
        # Título y controles
        header_frame = tk.Frame(students_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="Gestión de Estudiantes", 
                font=("Arial", 18, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        
        tk.Button(header_frame, text="➕ Nuevo Estudiante", 
                 command=self.register_new_student, bg="#4CAF50", fg="white",
                 font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(header_frame, text="🔄 Actualizar", 
                 command=self.refresh_students_list, bg="#2196F3", fg="white",
                 font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
        
        # Lista de estudiantes
        list_frame = tk.Frame(students_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para estudiantes
        columns = ("ID", "Nombre", "Asistencias", "Última Asistencia", "Rostros")
        self.students_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=150, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos iniciales
        self.refresh_students_list()
    
    def create_recognition_tab(self):
        """Crear pestaña de reconocimiento"""
        recognition_frame = ttk.Frame(self.notebook)
        self.notebook.add(recognition_frame, text="🎯 Reconocimiento")
        
        # Controles superiores
        controls_frame = tk.Frame(recognition_frame, bg="#f0f0f0")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(controls_frame, text="Reconocimiento Facial", 
                font=("Arial", 18, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        
        # Selección de aula
        tk.Label(controls_frame, text="Aula:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.RIGHT, padx=(0, 5))
        
        self.classroom_var = tk.StringVar(value=self.current_classroom)
        classroom_combo = ttk.Combobox(controls_frame, textvariable=self.classroom_var, 
                                     values=list(self.system.classrooms.keys()), state="readonly")
        classroom_combo.pack(side=tk.RIGHT, padx=5)
        
        # Botones de control
        buttons_frame = tk.Frame(recognition_frame, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = tk.Button(buttons_frame, text="🚀 Iniciar Reconocimiento", 
                                  command=self.start_recognition, bg="#4CAF50", fg="white",
                                  font=("Arial", 12, "bold"))
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(buttons_frame, text="⏹ Detener", 
                                 command=self.stop_recognition, bg="#f44336", fg="white",
                                 font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Área de video
        video_frame = tk.LabelFrame(recognition_frame, text="Vista de Cámara", 
                                   font=("Arial", 12, "bold"))
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.video_label = tk.Label(video_frame, text="Cámara no activa", 
                                   bg="black", fg="white", font=("Arial", 16))
        self.video_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Log de reconocimientos
        log_frame = tk.LabelFrame(recognition_frame, text="Log de Reconocimientos", 
                                 font=("Arial", 12, "bold"))
        log_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=6, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def create_attendance_tab(self):
        """Crear pestaña de asistencia"""
        attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(attendance_frame, text="📋 Asistencia")
        
        # Título y filtros
        header_frame = tk.Frame(attendance_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="Registros de Asistencia", 
                font=("Arial", 18, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        
        # Filtros
        filters_frame = tk.Frame(header_frame, bg="#f0f0f0")
        filters_frame.pack(side=tk.RIGHT)
        
        tk.Label(filters_frame, text="Fecha:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(filters_frame, textvariable=self.date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(filters_frame, text="🔍 Filtrar", 
                 command=self.filter_attendance, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Lista de asistencia
        list_frame = tk.Frame(attendance_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Estudiante", "Fecha", "Hora", "Aula", "Estado")
        self.attendance_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=120, anchor=tk.CENTER)
        
        # Scrollbar para asistencia
        att_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=att_scrollbar.set)
        
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        att_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos iniciales
        self.refresh_attendance_list()
    
    def create_settings_tab(self):
        """Crear pestaña de configuraciones"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Configuración")
        
        # Título
        tk.Label(settings_frame, text="Configuraciones del Sistema", 
                font=("Arial", 18, "bold")).pack(pady=20)
        
        # Frame principal de configuraciones
        config_frame = tk.LabelFrame(settings_frame, text="Configuraciones", 
                                   font=("Arial", 12, "bold"))
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Umbral de reconocimiento
        threshold_frame = tk.Frame(config_frame)
        threshold_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(threshold_frame, text="Umbral de Reconocimiento (%):").pack(side=tk.LEFT)
        self.threshold_var = tk.DoubleVar(value=self.system.settings.get("recognition_threshold", 75))
        threshold_scale = tk.Scale(threshold_frame, from_=50, to=95, orient=tk.HORIZONTAL,
                                 variable=self.threshold_var, resolution=5)
        threshold_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)
        
        # Cooldown
        cooldown_frame = tk.Frame(config_frame)
        cooldown_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(cooldown_frame, text="Cooldown entre registros (segundos):").pack(side=tk.LEFT)
        self.cooldown_var = tk.IntVar(value=self.system.settings.get("cooldown_seconds", 10))
        cooldown_spin = tk.Spinbox(cooldown_frame, from_=5, to=60, textvariable=self.cooldown_var)
        cooldown_spin.pack(side=tk.RIGHT)
        
        # Índice de cámara
        camera_frame = tk.Frame(config_frame)
        camera_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(camera_frame, text="Índice de Cámara:").pack(side=tk.LEFT)
        self.camera_var = tk.IntVar(value=self.system.settings.get("camera_index", 0))
        camera_spin = tk.Spinbox(camera_frame, from_=0, to=5, textvariable=self.camera_var)
        camera_spin.pack(side=tk.RIGHT)
        
        # Botones
        buttons_frame = tk.Frame(config_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=20)
        
        tk.Button(buttons_frame, text="💾 Guardar Configuración", 
                 command=self.save_settings, bg="#4CAF50", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="🔄 Re-entrenar Modelo", 
                 command=self.retrain_model, bg="#FF9800", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="🧪 Probar Cámara", 
                 command=self.test_camera, bg="#2196F3", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
    
    # Métodos de funcionalidad
    def refresh_students_list(self):
        """Actualizar lista de estudiantes"""
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        for student_id, student_data in self.system.students.items():
            self.students_tree.insert("", tk.END, values=(
                student_id,
                student_data["name"],
                student_data.get("total_attendance", 0),
                student_data.get("last_attendance", "Nunca"),
                len(student_data.get("face_files", []))
            ))
    
    def refresh_attendance_list(self):
        """Actualizar lista de asistencia"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Mostrar registros recientes (últimos 50)
        recent_records = sorted(self.system.attendance_records, 
                              key=lambda x: x["timestamp"], reverse=True)[:50]
        
        for record in recent_records:
            self.attendance_tree.insert("", tk.END, values=(
                record["student_name"],
                record["date"],
                record["time"],
                record["classroom_id"],
                record["status"]
            ))
    
    def register_new_student(self):
        """Registrar nuevo estudiante"""
        dialog = StudentRegistrationDialog(self.root, self.system)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.refresh_students_list()
            self.log_message(f"✅ Estudiante registrado: {dialog.result}")
    
    def quick_register_student(self):
        """Registro rápido de estudiante"""
        name = simpledialog.askstring("Registro Rápido", "Nombre del estudiante:")
        if name:
            success, message = self.system.register_student(name)
            if success:
                self.refresh_students_list()
                self.log_message(f"✅ {message}")
                messagebox.showinfo("Éxito", message)
            else:
                self.log_message(f"❌ Error: {message}")
                messagebox.showerror("Error", message)
    
    def start_recognition(self):
        """Iniciar reconocimiento facial"""
        if self.recognition_active:
            return
        
        self.current_classroom = self.classroom_var.get()
        
        if not self.system.initialize_camera():
            messagebox.showerror("Error", "No se pudo inicializar la cámara")
            return
        
        if not self.system.names_dict:
            if not self.system.load_trained_model():
                messagebox.showwarning("Advertencia", 
                                     "No hay modelo entrenado. Registre estudiantes primero.")
                return
        
        self.recognition_active = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.log_message(f"🚀 Reconocimiento iniciado en {self.current_classroom}")
        self.update_status("🔴 Reconocimiento activo", "red")
        
        # Iniciar thread de reconocimiento
        self.recognition_thread = threading.Thread(target=self.recognition_loop, daemon=True)
        self.recognition_thread.start()
    
    def stop_recognition(self):
        """Detener reconocimiento facial"""
        self.recognition_active = False
        self.system.release_camera()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.video_label.config(image="", text="Cámara detenida")
        self.log_message("⏹ Reconocimiento detenido")
        self.update_status("✅ Sistema listo", "green")
    
    def recognition_loop(self):
        """Loop principal de reconocimiento"""
        last_recognition = {}
        cooldown_time = self.system.settings.get("cooldown_seconds", 10)
        
        while self.recognition_active:
            try:
                ret, frame = self.system.camera.read()
                if not ret:
                    continue
                
                # Detectar rostros
                faces, gray = self.system.detect_faces(frame)
                
                current_time = time.time()
                
                for (x, y, w, h) in faces:
                    # Extraer ROI del rostro
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Reconocer rostro
                    name, confidence = self.system.recognize_face(face_roi)
                    
                    if name:
                        # Verificar cooldown
                        if (name not in last_recognition or 
                            current_time - last_recognition[name] > cooldown_time):
                            
                            # Marcar asistencia
                            success, message = self.system.mark_attendance(name, self.current_classroom)
                            
                            if success:
                                last_recognition[name] = current_time
                                
                                # Actualizar UI en main thread
                                self.root.after(0, lambda n=name, c=confidence: 
                                               self.on_recognition_success(n, c))
                        
                        # Dibujar rectángulo verde
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f"{name} ({confidence:.1f}%)", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        # Dibujar rectángulo rojo
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(frame, "Desconocido", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Mostrar información en pantalla
                cv2.putText(frame, f"Aula: {self.current_classroom}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"Estudiantes: {len(self.system.students)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Convertir frame para tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((640, 480), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Actualizar UI en main thread
                self.root.after(0, lambda p=photo: self.update_video_display(p))
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"Error en reconocimiento: {e}")
                time.sleep(0.1)
    
    def update_video_display(self, photo):
        """Actualizar display de video"""
        if self.recognition_active:
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # Mantener referencia
    
    def on_recognition_success(self, name, confidence):
        """Callback cuando se reconoce exitosamente"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_message(f"✅ {timestamp} - {name} reconocido ({confidence:.1f}%)")
        self.refresh_attendance_list()
    
    def filter_attendance(self):
        """Filtrar registros de asistencia por fecha"""
        target_date = self.date_var.get()
        
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        filtered_records = [r for r in self.system.attendance_records 
                          if r["date"] == target_date]
        
        for record in filtered_records:
            self.attendance_tree.insert("", tk.END, values=(
                record["student_name"],
                record["date"],
                record["time"],
                record["classroom_id"],
                record["status"]
            ))
    
    def save_settings(self):
        """Guardar configuraciones"""
        self.system.settings.update({
            "recognition_threshold": self.threshold_var.get(),
            "cooldown_seconds": self.cooldown_var.get(),
            "camera_index": self.camera_var.get()
        })
        
        self.system.save_settings()
        messagebox.showinfo("Éxito", "Configuraciones guardadas")
        self.log_message("⚙️ Configuraciones actualizadas")
    
    def retrain_model(self):
        """Re-entrenar modelo de reconocimiento"""
        if messagebox.askyesno("Confirmar", "¿Re-entrenar el modelo de reconocimiento?"):
            self.log_message("🔄 Re-entrenando modelo...")
            self.system.load_face_data()
            
            if self.system.train_recognizer():
                messagebox.showinfo("Éxito", "Modelo re-entrenado exitosamente")
                self.log_message("✅ Modelo re-entrenado")
            else:
                messagebox.showerror("Error", "No se pudo re-entrenar el modelo")
                self.log_message("❌ Error re-entrenando modelo")
    
    def test_camera(self):
        """Probar acceso a cámara"""
        if self.system.initialize_camera():
            messagebox.showinfo("Éxito", "Cámara accesible")
            self.system.release_camera()
            self.log_message("📷 Cámara probada exitosamente")
        else:
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            self.log_message("❌ Error accediendo a cámara")
    
    def export_report(self):
        """Exportar reporte de asistencia"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar reporte de asistencia"
            )
            
            if filename:
                # Crear DataFrame
                df = pd.DataFrame(self.system.attendance_records)
                df.to_csv(filename, index=False, encoding='utf-8')
                
                messagebox.showinfo("Éxito", f"Reporte exportado: {filename}")
                self.log_message(f"📊 Reporte exportado: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando reporte: {e}")
            self.log_message(f"❌ Error exportando: {e}")
    
    def log_message(self, message):
        """Agregar mensaje al log"""
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except:
            pass
    
    def update_status(self, message, color="black"):
        """Actualizar mensaje de estado"""
        try:
            self.status_label.config(text=message, fg=color)
        except:
            pass
    
    def run(self):
        """Ejecutar aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Manejar cierre de aplicación"""
        if self.recognition_active:
            self.stop_recognition()
        
        self.system.release_camera()
        self.root.destroy()

# Diálogo de registro de estudiante
class StudentRegistrationDialog:
    """Diálogo para registro detallado de estudiante"""
    
    def __init__(self, parent, system):
        self.parent = parent
        self.system = system
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Registrar Nuevo Estudiante")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Centrar diálogo
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(main_frame, text="Registro de Estudiante", 
                font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Nombre
        tk.Label(main_frame, text="Nombre completo:", font=("Arial", 12)).pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.name_var, font=("Arial", 12)).pack(fill=tk.X, pady=(5, 15))
        
        # Email
        tk.Label(main_frame, text="Email (opcional):", font=("Arial", 12)).pack(anchor=tk.W)
        self.email_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.email_var, font=("Arial", 12)).pack(fill=tk.X, pady=(5, 15))
        
        # Grado/Curso
        tk.Label(main_frame, text="Grado/Curso (opcional):", font=("Arial", 12)).pack(anchor=tk.W)
        self.grade_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.grade_var, font=("Arial", 12)).pack(fill=tk.X, pady=(5, 15))
        
        # Botones
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(buttons_frame, text="✅ Registrar", command=self.register,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="❌ Cancelar", command=self.cancel,
                 bg="#f44336", fg="white", font=("Arial", 12, "bold")).pack(side=tk.RIGHT, padx=5)
    
    def register(self):
        """Registrar estudiante"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        student_data = {
            "email": self.email_var.get().strip(),
            "grade": self.grade_var.get().strip()
        }
        
        success, message = self.system.register_student(name, student_data)
        
        if success:
            self.result = message
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", message)
    
    def cancel(self):
        """Cancelar registro"""
        self.dialog.destroy()

# Función principal
def main():
    """Función principal"""
    try:
        # Verificar dependencias
        print("Verificando dependencias...")
        
        # Verificar OpenCV
        if cv2.__version__:
            print(f"✅ OpenCV: {cv2.__version__}")
        
        # Verificar LBPH
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            print("✅ LBPH Face Recognizer disponible")
        except:
            print("❌ LBPH Face Recognizer no disponible")
            print("Instale: pip install opencv-contrib-python")
            return
        
        # Iniciar aplicación
        print("Iniciando AsistoYA...")
        app = AsistoYAGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario")
    except Exception as e:
        print(f"Error inesperado: {e}")
        messagebox.showerror("Error Fatal", f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
