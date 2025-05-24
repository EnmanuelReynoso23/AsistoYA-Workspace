import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import os
import time
import cv2
import numpy as np
from PIL import Image, ImageTk

from camera import Camera
from attendance import AttendanceManager
from notifications import NotificationManager
from database import Database
from security import Security
from face_recognition_manager import FaceRecognitionManager
from tkinter import Menu
from tkinter import messagebox
from models import SchoolManager

class UserInterface:
    def create_management_menu(self):
        menubar = tk.Menu(self.root)
        # Cursos
        course_menu = tk.Menu(menubar, tearoff=0)
        course_menu.add_command(label="Crear curso", command=self.prompt_create_course)
        course_menu.add_command(label="Seleccionar curso", command=self.prompt_select_course)
        menubar.add_cascade(label="Cursos", menu=course_menu)
        
        # Profesores
        prof_menu = tk.Menu(menubar, tearoff=0)
        prof_menu.add_command(label="Registrar profesor", command=self.prompt_register_professor)
        prof_menu.add_command(label="Asignar a curso", command=self.prompt_assign_professor)
        menubar.add_cascade(label="Profesores", menu=prof_menu)
        
        # Estudiantes
        student_menu = tk.Menu(menubar, tearoff=0)
        student_menu.add_command(label="Registrar estudiante", command=self.prompt_register_student)
        menubar.add_cascade(label="Estudiantes", menu=student_menu)
        
        # Reportes
        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="Exportar asistencia", command=self.export_attendance_report)
        menubar.add_cascade(label="Reportes", menu=report_menu)
        
        self.root.config(menu=menubar)
        
    def prompt_create_course(self):
        import tkinter.simpledialog as simpledialog
        name = simpledialog.askstring("Crear curso", "Nombre del curso:")
        if name:
            self.create_course(name)

    def prompt_select_course(self):
        import tkinter.simpledialog as simpledialog
        codes = list(self.school_manager.courses.keys())
        if not codes:
            messagebox.showinfo("Sin cursos", "Primero crea un curso.")
            return
        code = simpledialog.askstring("Seleccionar curso", f"Códigos disponibles: {', '.join(codes)}\nIngresa el código del curso:")
        if code and code in self.school_manager.courses:
            self.set_active_course(code)
            messagebox.showinfo("Curso seleccionado", f"Curso activo: {self.school_manager.courses[code].name}")
        else:
            messagebox.showwarning("Código inválido", "El código ingresado no corresponde a ningún curso.")

    def prompt_register_professor(self):
        import tkinter.simpledialog as simpledialog
        name = simpledialog.askstring("Registrar profesor", "Nombre:")
        surname = simpledialog.askstring("Registrar profesor", "Apellido:")
        email = simpledialog.askstring("Registrar profesor", "Email:")
        if name and surname and email:
            self.register_professor(name, surname, email)

    def prompt_register_student(self):
        import tkinter.simpledialog as simpledialog
        name = simpledialog.askstring("Registrar estudiante", "Nombre:")
        surname = simpledialog.askstring("Registrar estudiante", "Apellido:")
        email = simpledialog.askstring("Registrar estudiante", "Email:")
        if name and surname and email:
            self.register_student(name, surname, email)

    def prompt_assign_professor(self):
        """Muestra un diálogo para asignar un profesor a un curso"""
        import tkinter.simpledialog as simpledialog
        
        # Verificar que existan profesores y cursos
        if not self.school_manager.professors:
            messagebox.showwarning("Sin profesores", "No hay profesores registrados en el sistema")
            return
            
        if not self.school_manager.courses:
            messagebox.showwarning("Sin cursos", "No hay cursos creados en el sistema")
            return
            
        # Solicitar selección de profesor
        prof_codes = []
        for code, prof in self.school_manager.professors.items():
            prof_codes.append(f"{prof.full_name()} ({code})")
            
        professor_selection = simpledialog.askstring(
            "Seleccionar profesor", 
            f"Profesores disponibles:\n{', '.join(prof_codes)}\n\nIngrese el código del profesor:"
        )
        
        if not professor_selection or professor_selection not in self.school_manager.professors:
            messagebox.showwarning("Código inválido", "El código de profesor ingresado no es válido")
            return
            
        # Solicitar selección de curso
        course_codes = []
        for code, course in self.school_manager.courses.items():
            course_codes.append(f"{course.name} ({code})")
            
        course_selection = simpledialog.askstring(
            "Seleccionar curso", 
            f"Cursos disponibles:\n{', '.join(course_codes)}\n\nIngrese el código del curso:"
        )
        
        if not course_selection or course_selection not in self.school_manager.courses:
            messagebox.showwarning("Código inválido", "El código de curso ingresado no es válido")
            return
            
        # Asignar profesor al curso
        if self.school_manager.assign_professor_to_course(professor_selection, course_selection):
            prof_name = self.school_manager.professors[professor_selection].full_name()
            course_name = self.school_manager.courses[course_selection].name
            messagebox.showinfo(
                "Éxito",
                f"Profesor {prof_name} asignado al curso {course_name}"
            )
        else:
            messagebox.showerror("Error", "No se pudo asignar el profesor al curso")
            
    def __init__(self, root, database, security):
        self.root = root
        self.database = database
        self.security = security
        self.camera_index = 0
        self.camera = Camera(self.camera_index)
        self.attendance_manager = AttendanceManager(database)
        self.notification_manager = NotificationManager(api_url="https://api.whatsapp.com/send", api_key="YOUR_API_KEY")
        self.tooltip = None
        self.available_cameras = self.list_cameras()
        # --- SchoolManager integration ---
        self.school_manager = SchoolManager()
        self.active_course_code = None
        
        # Configuration properties
        self.face_confidence_threshold = 80  # Threshold for face recognition confidence
        self.send_notifications = False       # Whether to send notifications to tutors
        self.notification_label = None        # Label for displaying notifications
        self.capture_interval = 1000          # Milliseconds between attendance captures
        self.last_capture_time = 0            # Time of last attendance capture
        self.last_model_training_time = 0     # Time of last face model training
        self.model_training_interval = 60000  # Train model at most once every 60 seconds
        
        # Create data directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("faces", exist_ok=True)

    def create_course(self, name):
        course = self.school_manager.create_course(name)
        messagebox.showinfo("Curso creado", f"Curso '{name}' creado con código: {course.code}")
        return course

    def register_professor(self, name, surname, email):
        prof = self.school_manager.register_professor(name, surname, email)
        messagebox.showinfo("Profesor registrado", f"Profesor '{name} {surname}' registrado con código: {prof.code}")
        return prof

    def register_student(self, name, surname, email):
        student = self.school_manager.register_student(name, surname, email)
        messagebox.showinfo("Estudiante registrado", f"Estudiante '{name} {surname}' registrado con código: {student.code}")
        return student

    def set_active_course(self, course_code):
        self.active_course_code = course_code
        self.load_student_list()
    def list_cameras(self, max_tested=5):
        import cv2
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"Cam {i}")
                cap.release()
        # Permitir agregar cámara IP manualmente
        available.append("Cámara IP...")
        return available
        
    def load_main_interface(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_management_menu()
        self.create_main_interface()
        self.create_tooltips()
        self.create_context_menu()

    def create_main_interface(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Selector de cámara
        camera_select_frame = ttk.Frame(self.main_frame)
        camera_select_frame.pack(fill=tk.X, pady=5)
        ttk.Label(camera_select_frame, text="Seleccionar cámara:").pack(side=tk.LEFT, padx=5)
        self.camera_var = tk.StringVar(value=self.available_cameras[0])
        self.camera_menu = ttk.Combobox(camera_select_frame, values=self.available_cameras, textvariable=self.camera_var, width=15)
        self.camera_menu.pack(side=tk.LEFT)
        self.camera_menu.bind("<<ComboboxSelected>>", self.change_camera)

        self.create_camera_view()
        self.create_student_list()
        self.create_control_buttons()

    def change_camera(self, event=None):
        import cv2
        selected = self.camera_var.get()
        if selected == "Cámara IP...":
            import tkinter.simpledialog as simpledialog
            url = simpledialog.askstring("Cámara IP", "Introduce la URL del stream de la cámara IP (por ejemplo, rtsp o http):")
            if url:
                self.camera.capture.release()
                self.camera.capture = cv2.VideoCapture(url)
                self.camera_index = url
        else:
            idx = int(selected.replace("Cam ", ""))
            self.camera_index = idx
            self.camera.capture.release()
            self.camera.capture = cv2.VideoCapture(self.camera_index)

    def create_camera_view(self):
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)

        # Botón para guardar rostro
        self.save_face_button = ttk.Button(self.camera_frame, text="Guardar rostro con nombre", command=self.save_face_from_gui)
        self.save_face_button.pack(pady=5)

        self.update_camera_view()

    def save_face_from_gui(self):
        import cv2
        from face_recognition_manager import FaceRecognitionManager
        import tkinter.simpledialog as simpledialog
        
        # Capturar frame de la cámara
        gray = None
        frame = None
        ret, frame = self.camera.capture.read()
        if not ret:
            tk.messagebox.showwarning("Advertencia", "No se pudo acceder a la cámara.")
            return
            
        # Convertir a escala de grises para detección facial
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_manager = FaceRecognitionManager()
        faces = face_manager.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            tk.messagebox.showwarning("Advertencia", "No se detectó rostro para guardar.")
            return
            
        # Procesar el primer rostro detectado
        (x, y, w, h) = faces[0]
        face_img = gray[y:y+h, x:x+w]
        face_img_resized = cv2.resize(face_img, (200, 200))
        
        # Solicitar información del estudiante
        nombre = simpledialog.askstring("Guardar rostro", "Nombre:")
        if not nombre:
            return
            
        apellido = simpledialog.askstring("Guardar rostro", "Apellido:")
        if not apellido:
            return
            
        email = simpledialog.askstring("Guardar rostro", "Email (opcional):")
        
        # Verificar si ya existe un estudiante con ese nombre
        nombre_completo = f"{nombre} {apellido}"
        existing_student = None
        
        for code, student in self.school_manager.students.items():
            if student.full_name() == nombre_completo:
                existing_student = student
                break
                
        # Si no existe, crear nuevo estudiante
        if not existing_student:
            student = self.school_manager.register_student(nombre, apellido, email or "")
            code = student.code
        else:
            student = existing_student
            code = student.code
            
        # Guardar el rostro
        face_code = face_manager.save_face(face_img_resized, nombre_completo)
        
        # Asociar archivo de rostro al estudiante
        student.add_face(f"{nombre_completo}_{face_code}")
        
        # Preguntar si desea matricular al estudiante en el curso activo
        if self.active_course_code and messagebox.askyesno(
            "Matricular", 
            f"¿Desea matricular a {nombre_completo} en el curso activo?"
        ):
            self.school_manager.enroll_student_in_course(code, self.active_course_code)
            
        tk.messagebox.showinfo(
            "Éxito", 
            f"Rostro guardado como {nombre_completo}\nCódigo de estudiante: {code}"
        )        # Actualizar lista de estudiantes
        self.load_student_list()
        
    def update_camera_view(self):
        try:
            import cv2
            from face_recognition_manager import FaceRecognitionManager
            import numpy as np
            
            # Get frame from camera
            frame = self.camera.get_frame()
            if frame is not None:
                # Make a copy of the frame for display
                display_frame = frame.copy()
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Get face recognition manager
                face_manager = FaceRecognitionManager()
                
                # Detect faces using camera's detection method
                faces = self.camera.detect_faces(frame)
                recognized_students = set()  # Set of recognized student codes
                
                # Process each detected face
                for (x, y, w, h) in faces:
                    # Validate minimum face size
                    if w < 40 or h < 40:
                        continue
                        
                    # Extract and preprocess face
                    face_roi = gray[y:y+h, x:x+w]
                    try:
                        face_img = face_manager.preprocess_face(face_roi)
                    except Exception as e:
                        print(f"Error preprocessing face: {e}")
                        continue
                        
                    # Recognize face
                    name, conf = face_manager.recognize_face(face_img)
                    
                    # Handle recognized faces
                    if name != "Desconocido" and conf < self.face_confidence_threshold:
                        # Get student code from face manager
                        student_code = face_manager.get_student_code(name)
                        
                        # If no code associated with face, look up by name
                        if not student_code:
                            for code, student in self.school_manager.students.items():
                                if student.full_name() == name:
                                    student_code = code
                                    break
                        
                        # If student found and not already processed
                        if student_code and student_code not in recognized_students:
                            recognized_students.add(student_code)
                            
                            # Mark attendance if active course exists
                            if self.active_course_code:
                                # Get current time to determine if late
                                from datetime import datetime
                                current_time = datetime.now().time()
                                
                                # Check if course has a late threshold set (default 15 minutes)
                                status = "Presente"
                                if hasattr(self.school_manager.courses[self.active_course_code], 'late_threshold'):
                                    late_time = self.school_manager.courses[self.active_course_code].late_threshold
                                    if current_time > late_time:
                                        status = "Tardanza"
                                
                                # Mark attendance
                                self.school_manager.mark_attendance(
                                    self.active_course_code,
                                    student_code,
                                    status
                                )
                                
                                # Get student name for display
                                student_name = self.school_manager.students[student_code].full_name()
                                
                                # Show confirmation message
                                self.show_notification(f"✓ Asistencia registrada: {student_name}")
                                print(f"Attendance recorded: {student_name} in {self.active_course_code}")
                                
                                # Send notification to tutors if enabled
                                if self.send_notifications and self.notification_manager:
                                    student = self.school_manager.students[student_code]
                                    course_name = self.school_manager.courses[self.active_course_code].name
                                    
                                    for guardian in student.guardian_contacts:
                                        if "email" in guardian or "phone" in guardian:
                                            self.notification_manager.send_tutor_notification(
                                                guardian,
                                                student_name,
                                                status,
                                                course_name
                                            )
                            else:
                                # If no active course, use previous system
                                self.attendance_manager.mark_attendance(name, "presente")
                            
                            # Display the name with green rectangle
                            display_name = name
                            if student_code and student_code in self.school_manager.students:
                                display_name = self.school_manager.students[student_code].full_name()
                            
                            cv2.putText(display_frame, f"{display_name} ({conf:.0f})", 
                                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0,255,0), 2)
                        else:
                            # Already processed, just show name
                            display_name = name
                            if student_code and student_code in self.school_manager.students:
                                display_name = self.school_manager.students[student_code].full_name()
                            
                            cv2.putText(display_frame, display_name, 
                                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0,255,0), 2)
                    else:
                        # Unknown face
                        cv2.putText(display_frame, f"Desconocido ({conf:.0f})", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0,0,255), 2)
                
                # Update student list if new students were recognized
                if recognized_students and self.active_course_code:
                    self.load_student_list()
                
                # Add status overlay to the frame
                self.add_status_overlay(display_frame)
                
                # Convert to tkinter-compatible format and display
                from PIL import Image, ImageTk
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                tk_img = ImageTk.PhotoImage(image=pil_img)
                self.camera_label.imgtk = tk_img
                self.camera_label.configure(image=tk_img)
        except Exception as e:
            print(f"Error updating camera view: {e}")
            import traceback
            traceback.print_exc()
            
        # Schedule next update
        self.root.after(33, self.update_camera_view)  # ~30 FPS
        
    def add_status_overlay(self, frame):
        """Add status information overlay to the camera frame"""
        if frame is None:
            return
            
        # Add semi-transparent overlay at the bottom
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h-60), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Add status information
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        
        # Show active course
        if self.active_course_code:
            course_text = f"Curso: {self.school_manager.courses[self.active_course_code].name}"
        else:
            course_text = "Sin curso activo"
        cv2.putText(frame, course_text, (10, h-40), font, font_scale, (255, 255, 255), 1)
        
        # Show camera status
        camera_status = f"Cámara: {self.camera_index}"
        cv2.putText(frame, camera_status, (10, h-20), font, font_scale, (255, 255, 255), 1)
        
        # Show attendance mode and count
        if self.active_course_code:
            course = self.school_manager.courses[self.active_course_code]
            today = datetime.now().strftime("%Y-%m-%d")
            
            attendance_count = 0
            if today in course.attendance:
                attendance_count = len(course.attendance[today])
                
            attendance_text = f"Asistencias hoy: {attendance_count}/{len(course.students)}"
            cv2.putText(frame, attendance_text, (w-200, h-20), font, font_scale, (255, 255, 255), 1)
            
    def show_notification(self, message, duration=3000):
        """Show a temporary notification message"""
        try:
            if hasattr(self, 'notification_label'):
                self.notification_label.destroy()
                
            self.notification_label = ttk.Label(
                self.camera_frame, 
                text=message,
                font=("Arial", 12),
                padding=10,
                bootstyle="success"
            )
            self.notification_label.pack(pady=10)
            
            # Schedule removal
            self.root.after(duration, lambda: self.hide_notification())
        except Exception as e:
            print(f"Error showing notification: {e}")
            
    def hide_notification(self):
        """Hide the notification message"""
        try:
            if hasattr(self, 'notification_label'):
                self.notification_label.destroy()
                self.notification_label = None
        except Exception as e:
            print(f"Error hiding notification: {e}")

    def create_student_list(self):
        self.student_list_frame = ttk.Frame(self.main_frame)
        self.student_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.student_list = ttk.Treeview(self.student_list_frame, columns=("ID", "Name", "Status", "Code"), show="headings")
        self.student_list.heading("ID", text="ID")
        self.student_list.heading("Name", text="Name")
        self.student_list.heading("Status", text="Status")
        self.student_list.heading("Code", text="Código")
        self.student_list.pack(fill=tk.BOTH, expand=True)

        self.load_student_list()

    def load_student_list(self):
        # Limpiar la lista actual
        for item in self.student_list.get_children():
            self.student_list.delete(item)
            
        # Si hay un curso activo, mostrar sus estudiantes
        if self.active_course_code and self.active_course_code in self.school_manager.courses:
            course = self.school_manager.courses[self.active_course_code]
            date_today = datetime.now().strftime("%Y-%m-%d")
            
            for student_code, student in course.students.items():
                # Verificar si hay registro de asistencia para hoy
                status = "Sin registro"
                if date_today in course.attendance and student_code in course.attendance[date_today]:
                    status = course.attendance[date_today][student_code]
                
                self.student_list.insert("", "end", values=(
                    student_code, 
                    student.full_name(), 
                    status,
                    student_code
                ))
        # Si no hay curso activo o hay base de datos, usar el método anterior
        elif self.database:
            students = self.database.get_all_students()
            for student in students:
                code = student.get("code", "")
                self.student_list.insert("", "end", values=(student["id"], student["name"], student["status"], code))
        else:
            # Leer de los registros de asistencia en memoria para mostrar los estudiantes y sus códigos
            seen = set()
            students = []
            for record in self.attendance_manager.attendance_records:
                sid = record["Student ID"]
                code = record.get("Code", "")
                # Separar nombre y código si están juntos
                if "_" in sid and code == "":
                    nombre, code = sid.rsplit("_", 1)
                else:
                    nombre = sid
                if sid not in seen:
                    students.append({
                        "id": sid,
                        "name": nombre,
                        "status": record["Status"],
                        "code": code
                    })
                    seen.add(sid)
            for student in students:
                self.student_list.insert("", "end", values=(student["id"], student["name"], student["status"], student["code"]))

    def create_control_buttons(self):
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_button = ttk.Button(self.control_frame, text="Iniciar sesión", command=self.start_attendance_session)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = ttk.Button(self.control_frame, text="Pausar", command=self.pause_attendance_session)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = ttk.Button(self.control_frame, text="Finalizar sesión", command=self.stop_attendance_session)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Nuevos botones para gestión de asistencia
        self.mark_button = ttk.Button(self.control_frame, text="Marcar manualmente", command=self.mark_attendance_manually)
        self.mark_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.export_button = ttk.Button(self.control_frame, text="Exportar reporte", command=self.export_attendance_report)
        self.export_button.pack(side=tk.LEFT, padx=5, pady=5)

    def start_attendance_session(self):
        self.attendance_manager.start_session()

    def pause_attendance_session(self):
        self.attendance_manager.pause_session()

    def stop_attendance_session(self):
        self.attendance_manager.stop_session()

    def update_student_status(self, student_id, status):
        self.attendance_manager.mark_attendance(student_id, status)
        self.load_student_list()

    def send_notification(self, phone_number, template, student_name):
        self.notification_manager.send_notification(phone_number, template, student_name)

    def view_notification_history(self):
        history = self.notification_manager.get_notification_history()
        for record in history:
            print(f"{record['timestamp']}: {record['phone_number']} - {record['message']}")

    def create_tooltips(self):
        self.tooltips = {
            self.start_button: "Start the attendance session",
            self.pause_button: "Pause the attendance session",
            self.stop_button: "Stop the attendance session"
        }
        for widget, text in self.tooltips.items():
            widget.bind("<Enter>", lambda e, t=text: self.show_tooltip(e, t))
            widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, text):
        x, y, _, _ = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(event.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()

    def create_context_menu(self):
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Editar estudiante", command=self.edit_student)
        self.context_menu.add_command(label="Eliminar estudiante", command=self.delete_student)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Marcar asistencia", command=self.mark_attendance_manually)
        self.context_menu.add_command(label="Generar código para tutor", command=self.generate_tutor_access_code)
        
        # Submenú para asignar a curso (si no está en el curso activo)
        self.course_assign_menu = Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Asignar a curso", menu=self.course_assign_menu)
        
        self.student_list.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        # Verificar si hay algún elemento seleccionado
        selected_items = self.student_list.selection()
        if not selected_items:
            return
            
        # Obtener estudiante seleccionado
        student_code = self.student_list.item(selected_items[0], "values")[0]
        
        # Actualizar menú de cursos disponibles
        self.course_assign_menu.delete(0, 'end')
        for code, course in self.school_manager.courses.items():
            # Si no es el curso activo y el estudiante no está matriculado en él
            if (not self.active_course_code or code != self.active_course_code) and \
               (student_code not in course.students):
                self.course_assign_menu.add_command(
                    label=f"{course.name} ({code})",
                    command=lambda c=code, s=student_code: self.assign_student_to_course(s, c)
                )
        
        # Mostrar el menú contextual
        self.context_menu.post(event.x_root, event.y_root)

    def edit_student(self):
        """Editar información de un estudiante"""
        import tkinter.simpledialog as simpledialog
        
        selected_items = self.student_list.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Debe seleccionar un estudiante para editar")
            return
            
        student_code = self.student_list.item(selected_items[0], "values")[0]
        
        # Verificar que el estudiante existe en el sistema
        if student_code not in self.school_manager.students:
            messagebox.showerror("Error", "El estudiante seleccionado no se encuentra en el sistema")
            return
            
        student = self.school_manager.students[student_code]
        
        # Solicitar nueva información
        new_name = simpledialog.askstring("Editar estudiante", "Nombre:", initialvalue=student.name)
        if new_name is None:
            return
            
        new_surname = simpledialog.askstring("Editar estudiante", "Apellido:", initialvalue=student.surname)
        if new_surname is None:
            return
            
        new_email = simpledialog.askstring("Editar estudiante", "Email:", initialvalue=student.email)
        if new_email is None:
            return
            
        # Actualizar información
        student.name = new_name
        student.surname = new_surname
        student.email = new_email
        
        messagebox.showinfo("Éxito", "Información del estudiante actualizada correctamente")
        self.load_student_list()

    def delete_student(self):
        """Eliminar un estudiante del curso activo"""
        selected_items = self.student_list.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Debe seleccionar un estudiante para eliminar")
            return
            
        student_code = self.student_list.item(selected_items[0], "values")[0]
        
        # Verificar que estamos en un curso activo
        if not self.active_course_code:
            messagebox.showwarning("Advertencia", "Debe seleccionar un curso primero")
            return
            
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", "¿Está seguro de querer eliminar a este estudiante del curso?"):
            return
            
        # Eliminar estudiante del curso (pero no del sistema)
        course = self.school_manager.courses[self.active_course_code]
        if student_code in course.students:
            student = course.students[student_code]
            # Eliminar la referencia cruzada
            del course.students[student_code]
            if course.code in student.courses:
                del student.courses[course.code]
                
            messagebox.showinfo("Éxito", f"Estudiante eliminado del curso {course.name}")
            self.load_student_list()

    def assign_student_to_course(self, student_code, course_code):
        """Asigna un estudiante a un curso específico"""
        if self.school_manager.enroll_student_in_course(student_code, course_code):
            course_name = self.school_manager.courses[course_code].name
            student_name = self.school_manager.students[student_code].full_name()
            messagebox.showinfo(
                "Éxito", 
                f"Estudiante {student_name} matriculado exitosamente en el curso {course_name} ({course_code})"
            )
            # Actualizar lista si el curso asignado es el activo
            if course_code == self.active_course_code:
                self.load_student_list()
        else:
            messagebox.showerror("Error", "No se pudo matricular al estudiante en el curso seleccionado.")

    def mark_attendance_manually(self):
        selected_items = self.student_list.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Seleccione al menos un estudiante")
            return
            
        if not self.active_course_code:
            messagebox.showwarning("Advertencia", "Primero debe seleccionar un curso")
            return
            
        # Preguntar por el estado de asistencia
        import tkinter.simpledialog as simpledialog
        status = simpledialog.askstring(
            "Estado de asistencia", 
            "Ingrese el estado (Presente, Ausente, Tardanza):"
        )
        
        if not status:
            return
            
        # Marcar asistencia para cada estudiante seleccionado
        for item in selected_items:
            student_code = self.student_list.item(item, "values")[0]
            self.school_manager.mark_attendance(
                self.active_course_code,
                student_code,
                status
            )
            
        messagebox.showinfo("Éxito", "Asistencia registrada correctamente")
        self.load_student_list()

    def export_attendance_report(self):
        if not self.active_course_code:
            messagebox.showwarning("Advertencia", "Primero debe seleccionar un curso")
            return
            
        # Preguntar por el formato de exportación
        import tkinter.simpledialog as simpledialog
        formats = ["excel", "pdf"]
        format_str = simpledialog.askstring(
            "Formato de exportación", 
            f"Seleccione el formato ({'/'.join(formats)}):"
        )
        
        if not format_str or format_str.lower() not in formats:
            messagebox.showwarning("Formato inválido", f"Debe seleccionar entre {', '.join(formats)}")
            return
            
        # Exportar el reporte
        course = self.school_manager.courses[self.active_course_code]
        filename, message = course.export_attendance_report(format_str.lower())
        
        if filename:
            messagebox.showinfo("Éxito", f"{message}. Archivo guardado como {filename}")
        else:
            messagebox.showwarning("Error", message)

    def generate_tutor_access_code(self):
        """Genera un código de acceso para el tutor del estudiante seleccionado"""
        import tkinter.simpledialog as simpledialog
        
        # Verificar si hay un estudiante seleccionado
        selected_items = self.student_list.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Debe seleccionar un estudiante")
            return
            
        student_code = self.student_list.item(selected_items[0], "values")[0]
        
        # Verificar si el estudiante existe en el sistema
        if student_code not in self.school_manager.students:
            messagebox.showerror("Error", "El estudiante seleccionado no se encuentra en el sistema")
            return
            
        # Obtener duración del código de acceso
        duration = simpledialog.askinteger(
            "Duración del código", 
            "Ingrese la duración del código de acceso en horas:",
            initialvalue=24,
            minvalue=1,
            maxvalue=168  # máximo 1 semana
        )
        
        if not duration:
            return
            
        # Generar código de acceso
        try:
            access_code = self.security.generate_tutor_access_code(
                student_id=student_code,
                course_id=self.active_course_code,
                expiration_hours=duration
            )
            
            # Mostrar el código generado
            student_name = self.school_manager.students[student_code].full_name()
            expiration_time = self.security.tutor_access_codes[access_code]['expiration']
            
            from datetime import datetime
            expiration_date = datetime.fromtimestamp(expiration_time).strftime("%d/%m/%Y %H:%M")
            
            # Mostrar dialogo con el código
            messagebox.showinfo(
                "Código de Acceso Generado",
                f"CÓDIGO DE ACCESO PARA TUTOR\n\n"
                f"Estudiante: {student_name}\n"
                f"Código: {access_code}\n"
                f"Válido hasta: {expiration_date}\n\n"
                f"Comparta este código con el tutor del estudiante para\n"
                f"que pueda acceder a la información de asistencia."
            )
            
            # Registrar la generación del código en la base de datos o sistema de logs
            print(f"[INFO] Código de acceso {access_code} generado para tutor de {student_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el código de acceso: {e}")
            print(f"[ERROR] Error generando código de acceso: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    database = Database("asisto_ya.db")
    security = Security()
    ui = UserInterface(root, database, security)
    root.mainloop()
