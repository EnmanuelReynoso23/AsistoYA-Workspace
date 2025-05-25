import cv2
import os
import numpy as np
import time
import random
import string
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import threading
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class AdvancedFaceAttendanceSystem:
    def __init__(self):
        self.faces_dir = "faces"
        self.reports_dir = "reports"
        self.backup_dir = "backup"
        
        # Create directories
        for directory in [self.faces_dir, self.reports_dir, self.backup_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Storage files
        self.users_file = os.path.join(self.faces_dir, "registered_users.json")
        self.attendance_file = os.path.join(self.faces_dir, "attendance_records.json")
        self.settings_file = os.path.join(self.faces_dir, "app_settings.json")
        
        # Load data
        self.registered_users = self.load_registered_users()
        self.attendance_records = self.load_attendance_records()
        self.settings = self.load_settings()
        
        # Camera setup
        self.camera = None
        self.camera_index = 0
        self.setup_camera()
        
        # Face recognition data
        self.face_encodings = {}
        self.load_face_encodings()
        
        # Recognition cooldown to prevent spam
        self.last_recognition_time = {}
        self.recognition_cooldown = 5  # seconds
        
    def load_settings(self):
        """Load application settings"""
        default_settings = {
            "recognition_threshold": 0.6,
            "camera_resolution": [640, 480],
            "auto_backup": True,
            "sound_notifications": True,
            "attendance_timeout": 8,  # hours
            "max_faces_per_user": 3
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**default_settings, **settings}
            return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
    
    def save_settings(self):
        """Save application settings"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_registered_users(self):
        """Load registered users from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading registered users: {e}")
            return {}
    
    def save_registered_users(self):
        """Save registered users to file"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.registered_users, f, ensure_ascii=False, indent=2)
            
            # Auto backup if enabled
            if self.settings.get("auto_backup", True):
                self.create_backup()
                
        except Exception as e:
            print(f"Error saving registered users: {e}")
    
    def load_attendance_records(self):
        """Load attendance records from file"""
        try:
            if os.path.exists(self.attendance_file):
                with open(self.attendance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading attendance records: {e}")
            return []
    
    def save_attendance_records(self):
        """Save attendance records to file"""
        try:
            with open(self.attendance_file, 'w', encoding='utf-8') as f:
                json.dump(self.attendance_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving attendance records: {e}")
    
    def create_backup(self):
        """Create backup of all data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_folder, exist_ok=True)
            
            # Copy JSON files
            import shutil
            if os.path.exists(self.users_file):
                shutil.copy2(self.users_file, os.path.join(backup_folder, "registered_users.json"))
            if os.path.exists(self.attendance_file):
                shutil.copy2(self.attendance_file, os.path.join(backup_folder, "attendance_records.json"))
            
            print(f"Backup created: {backup_folder}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def setup_camera(self):
        """Initialize camera with advanced settings"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Configure camera
            resolution = self.settings.get("camera_resolution", [640, 480])
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 0.6)
            self.camera.set(cv2.CAP_PROP_CONTRAST, 0.6)
            self.camera.set(cv2.CAP_PROP_SATURATION, 0.6)
            return True
        except Exception as e:
            print(f"Error setting up camera: {e}")
            return False
    
    def change_camera(self, new_index):
        """Change camera source"""
        if self.camera:
            self.camera.release()
        
        self.camera_index = new_index
        return self.setup_camera()
    
    def get_available_cameras(self):
        """Get list of available cameras"""
        available_cameras = []
        for i in range(5):  # Check first 5 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras
    
    def generate_user_code(self, name):
        """Generate a unique code for the user"""
        parts = name.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[1][0].upper()
        else:
            initials = name[:2].upper()
        
        code = initials + ''.join(random.choices(string.digits, k=4))
        
        while any(user_data.get('code') == code for user_data in self.registered_users.values()):
            code = initials + ''.join(random.choices(string.digits, k=4))
        
        return code
    
    def preprocess_face(self, face_img):
        """Advanced face preprocessing"""
        try:
            # Resize to standard size
            face_img = cv2.resize(face_img, (200, 200))
            
            # Convert to grayscale if not already
            if len(face_img.shape) > 2:
                face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            
            # Apply advanced preprocessing
            face_img = cv2.equalizeHist(face_img)
            face_img = cv2.GaussianBlur(face_img, (3, 3), 0)
            
            return face_img
        except Exception as e:
            print(f"Error preprocessing face: {e}")
            return face_img
    
    def load_face_encodings(self):
        """Load all face encodings for recognition"""
        self.face_encodings = {}
        for name, user_data in self.registered_users.items():
            face_files = user_data.get('face_files', [])
            if not face_files and user_data.get('face_file'):  # Backward compatibility
                face_files = [user_data.get('face_file')]
            
            user_encodings = []
            for face_file in face_files:
                if face_file and os.path.exists(os.path.join(self.faces_dir, face_file)):
                    try:
                        face_img = cv2.imread(os.path.join(self.faces_dir, face_file), cv2.IMREAD_GRAYSCALE)
                        if face_img is not None:
                            user_encodings.append(face_img)
                    except Exception as e:
                        print(f"Error loading face encoding for {name}: {e}")
            
            if user_encodings:
                self.face_encodings[name] = user_encodings
    
    def recognize_face(self, face_img):
        """Advanced face recognition with multiple templates"""
        face_processed = self.preprocess_face(face_img)
        
        best_match = None
        best_score = 0
        threshold = self.settings.get("recognition_threshold", 0.6)
        
        for name, templates in self.face_encodings.items():
            max_score = 0
            
            # Check against all templates for this user
            for template in templates:
                try:
                    result = cv2.matchTemplate(face_processed, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    max_score = max(max_score, max_val)
                except Exception as e:
                    print(f"Error matching face with {name}: {e}")
                    continue
            
            if max_score > threshold and max_score > best_score:
                best_score = max_score
                best_match = name
        
        if best_match:
            confidence = best_score * 100
            return best_match, confidence
        
        return None, 0
    
    def register_user(self, name, face_img, department="", position="", email=""):
        """Register a new user with additional info"""
        if name in self.registered_users:
            # Add additional face if under limit
            max_faces = self.settings.get("max_faces_per_user", 3)
            current_faces = len(self.registered_users[name].get('face_files', []))
            
            if current_faces < max_faces:
                return self.add_face_to_user(name, face_img)
            else:
                return None, f"Error: User '{name}' already has maximum number of faces ({max_faces})"
        
        # Generate unique code
        user_code = self.generate_user_code(name)
        
        # Save face data
        timestamp = int(time.time())
        face_filename = f"{name.replace(' ', '_')}_{user_code}_{timestamp}.jpg"
        face_filepath = os.path.join(self.faces_dir, face_filename)
        
        processed_face = self.preprocess_face(face_img)
        cv2.imwrite(face_filepath, processed_face)
        
        # Register user with extended info
        user_data = {
            'name': name,
            'code': user_code,
            'department': department,
            'position': position,
            'email': email,
            'registration_date': datetime.now().isoformat(),
            'face_files': [face_filename],
            'total_attendance': 0,
            'last_attendance': None
        }
        
        self.registered_users[name] = user_data
        self.save_registered_users()
        
        # Update face encodings
        if name not in self.face_encodings:
            self.face_encodings[name] = []
        self.face_encodings[name].append(processed_face)
        
        print(f"User '{name}' registered successfully with code: {user_code}")
        return user_code, f"User '{name}' registered successfully!"
    
    def add_face_to_user(self, name, face_img):
        """Add additional face to existing user"""
        if name not in self.registered_users:
            return None, "User not found"
        
        # Save additional face
        timestamp = int(time.time())
        user_code = self.registered_users[name]['code']
        face_filename = f"{name.replace(' ', '_')}_{user_code}_{timestamp}_alt.jpg"
        face_filepath = os.path.join(self.faces_dir, face_filename)
        
        processed_face = self.preprocess_face(face_img)
        cv2.imwrite(face_filepath, processed_face)
        
        # Update user data
        if 'face_files' not in self.registered_users[name]:
            self.registered_users[name]['face_files'] = []
        
        self.registered_users[name]['face_files'].append(face_filename)
        self.save_registered_users()
        
        # Update face encodings
        if name not in self.face_encodings:
            self.face_encodings[name] = []
        self.face_encodings[name].append(processed_face)
        
        return user_code, f"Additional face added for {name}"
    
    def mark_attendance(self, name, attendance_type="Present"):
        """Mark attendance with cooldown and extended info"""
        if name not in self.registered_users:
            return False, "User not registered"
        
        current_time = time.time()
        
        # Check cooldown
        if name in self.last_recognition_time:
            time_diff = current_time - self.last_recognition_time[name]
            if time_diff < self.recognition_cooldown:
                return False, f"Please wait {self.recognition_cooldown - int(time_diff)} seconds"
        
        today = datetime.now().strftime("%Y-%m-%d")
        current_time_str = datetime.now().strftime("%H:%M:%S")
        
        # Check if already marked today
        for record in self.attendance_records:
            if record['name'] == name and record['date'] == today:
                return False, f"Attendance already marked for {name} today at {record['time']}"
        
        # Add attendance record
        attendance_record = {
            'name': name,
            'code': self.registered_users[name]['code'],
            'date': today,
            'time': current_time_str,
            'status': attendance_type,
            'department': self.registered_users[name].get('department', ''),
            'method': 'Facial Recognition'
        }
        
        self.attendance_records.append(attendance_record)
        self.save_attendance_records()
        
        # Update user statistics
        self.registered_users[name]['total_attendance'] += 1
        self.registered_users[name]['last_attendance'] = today
        self.save_registered_users()
        
        # Update cooldown
        self.last_recognition_time[name] = current_time
        
        return True, f"Attendance marked for {name} at {current_time_str}"
    
    def get_attendance_statistics(self):
        """Get comprehensive attendance statistics"""
        stats = {
            'total_users': len(self.registered_users),
            'total_records': len(self.attendance_records),
            'today_attendance': 0,
            'this_week_attendance': 0,
            'this_month_attendance': 0,
            'attendance_by_department': {},
            'daily_attendance_trend': []
        }
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Calculate daily trend for last 30 days
        for i in range(30):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            count = len([r for r in self.attendance_records if r['date'] == date_str])
            stats['daily_attendance_trend'].append({'date': date_str, 'count': count})
        
        for record in self.attendance_records:
            record_date = datetime.strptime(record['date'], "%Y-%m-%d").date()
            
            # Today's attendance
            if record_date == today:
                stats['today_attendance'] += 1
            
            # This week's attendance
            if record_date >= week_start:
                stats['this_week_attendance'] += 1
            
            # This month's attendance
            if record_date >= month_start:
                stats['this_month_attendance'] += 1
            
            # Department statistics
            dept = record.get('department', 'Unknown')
            if dept not in stats['attendance_by_department']:
                stats['attendance_by_department'][dept] = 0
            stats['attendance_by_department'][dept] += 1
        
        return stats
    
    def export_to_excel(self, start_date=None, end_date=None):
        """Export attendance records to Excel"""
        try:
            records = self.attendance_records.copy()
            
            # Filter by date range if provided
            if start_date or end_date:
                filtered_records = []
                for record in records:
                    record_date = datetime.strptime(record['date'], "%Y-%m-%d").date()
                    if start_date and record_date < start_date:
                        continue
                    if end_date and record_date > end_date:
                        continue
                    filtered_records.append(record)
                records = filtered_records
            
            if not records:
                return False, "No records found for the specified date range"
            
            # Create DataFrame
            df = pd.DataFrame(records)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.reports_dir, f"attendance_report_{timestamp}.xlsx")
            
            # Export to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Attendance Records', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Total Records': [len(records)],
                    'Unique Users': [len(set(r['name'] for r in records))],
                    'Date Range': [f"{records[0]['date']} to {records[-1]['date']}"],
                    'Export Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return True, f"Report exported to {filename}"
        
        except Exception as e:
            return False, f"Error exporting to Excel: {e}"
    
    def get_registered_users_list(self):
        """Get enhanced list of registered users"""
        users_list = []
        for name, data in self.registered_users.items():
            users_list.append({
                'name': name,
                'code': data['code'],
                'department': data.get('department', ''),
                'position': data.get('position', ''),
                'registration_date': data['registration_date'],
                'total_attendance': data.get('total_attendance', 0),
                'last_attendance': data.get('last_attendance', 'Never')
            })
        return users_list
    
    def get_attendance_records(self, date=None, department=None, user=None):
        """Get filtered attendance records"""
        records = self.attendance_records.copy()
        
        if date:
            records = [r for r in records if r['date'] == date]
        
        if department:
            records = [r for r in records if r.get('department', '') == department]
        
        if user:
            records = [r for r in records if r['name'] == user]
        
        return records
    
    def delete_user(self, name):
        """Delete a user and their data"""
        if name not in self.registered_users:
            return False, "User not found"
        
        try:
            # Delete face files
            face_files = self.registered_users[name].get('face_files', [])
            for face_file in face_files:
                file_path = os.path.join(self.faces_dir, face_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove from registered users
            del self.registered_users[name]
            self.save_registered_users()
            
            # Remove from face encodings
            if name in self.face_encodings:
                del self.face_encodings[name]
            
            return True, f"User {name} deleted successfully"
        
        except Exception as e:
            return False, f"Error deleting user: {e}"
    
    def release_camera(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

class AdvancedAttendanceApp:
    def create_settings_tab(self):
        pass
    # --- PLACEHOLDER METHODS FOR UI BUTTONS AND CONTEXT MENU ---
    def view_user_details(self):
        messagebox.showinfo("Detalles", "Funcionalidad no implementada.")

    def add_face_to_selected_user(self):
        messagebox.showinfo("Agregar Rostro", "Funcionalidad no implementada.")

    def delete_selected_user(self):
        messagebox.showinfo("Eliminar Usuario", "Funcionalidad no implementada.")

    def refresh_users_list(self):
        pass

    def create_attendance_tab(self):
        pass

    def create_reports_tab(self):
        pass

    def create_analytics_tab(self):
        pass
    def create_analytics_tab(self):
        """Crear pestaña de analíticas (placeholder)"""
        pass
    def create_reports_tab(self):
        """Crear pestaña de reportes (placeholder)"""
        pass
    def create_attendance_tab(self):
        """Crear pestaña de asistencia (placeholder)"""
        pass
    def view_user_details(self):
        """Mostrar detalles del usuario seleccionado (placeholder)"""
        messagebox.showinfo("Detalles de usuario", "Funcionalidad no implementada.")

    def add_face_to_selected_user(self):
        """Agregar rostro al usuario seleccionado (placeholder)"""
        messagebox.showinfo("Agregar rostro", "Funcionalidad no implementada.")

    def delete_selected_user(self):
        """Eliminar usuario seleccionado (placeholder)"""
        messagebox.showinfo("Eliminar usuario", "Funcionalidad no implementada.")

    def refresh_users_list(self):
        """Actualizar lista de usuarios (placeholder)"""
        pass
    def filter_users(self, event=None):
        """Filtrar usuarios en la lista (placeholder)"""
        # Aquí se implementaría la lógica de filtrado
        pass
    def add_additional_face(self):
        """Agregar un rostro adicional a un usuario (placeholder)"""
        messagebox.showinfo("Agregar Rostro", "Funcionalidad para agregar rostro adicional aún no implementada.")
    def register_user(self):
        """Registrar un nuevo usuario desde la interfaz"""
        messagebox.showinfo("Registro", "Funcionalidad de registro de usuario aún no implementada.")
    def start_camera(self):
        """Iniciar la cámara para registro de usuario"""
        try:
            self.recognition_active = True
            self.start_camera_display()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la cámara: {e}")

    def stop_camera(self):
        """Detener la cámara para registro de usuario"""
        try:
            self.recognition_active = False
            self.stop_camera_display()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo detener la cámara: {e}")
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Avanzado de Registro y Asistencia Facial")
        
        # Configure window
        width, height = 1200, 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Initialize face system
        self.face_system = AdvancedFaceAttendanceSystem()
        
        # Camera variables
        self.camera_running = False
        self.attendance_camera_running = False
        self.current_frame = None
        self.photo = None
        
        # Create UI
        self.create_interface()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_interface(self):
        """Create the enhanced interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enhanced tabs
        self.create_dashboard_tab()
        self.create_registration_tab()
        self.create_attendance_tab()
        self.create_reports_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with statistics"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Main container
        main_container = ttk.Frame(dashboard_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_container, text="Dashboard de Asistencia", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=(0, 30))
        
        # Statistics cards
        stats_frame = ttk.Frame(main_container)
        stats_frame.pack(fill=tk.X, pady=20)
        
        # Get statistics
        stats = self.face_system.get_attendance_statistics()
        
        # Create stat cards
        self.create_stat_card(stats_frame, "Usuarios Registrados", stats['total_users'], "👥")
        self.create_stat_card(stats_frame, "Asistencia Hoy", stats['today_attendance'], "📅")
        self.create_stat_card(stats_frame, "Esta Semana", stats['this_week_attendance'], "📊")
        self.create_stat_card(stats_frame, "Este Mes", stats['this_month_attendance'], "📈")
        
        # Quick actions
        actions_frame = ttk.LabelFrame(main_container, text="Acciones Rápidas", padding=20)
        actions_frame.pack(fill=tk.X, pady=20)
        
        actions_row = ttk.Frame(actions_frame)
        actions_row.pack(fill=tk.X)
        
        ttk.Button(actions_row, text="🔍 Reconocimiento Rápido", 
                  command=self.quick_recognition, bootstyle="success").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_row, text="📋 Exportar Hoy", 
                  command=self.export_today, bootstyle="info").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_row, text="🔄 Actualizar Dashboard", 
                  command=self.refresh_dashboard, bootstyle="primary").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_row, text="💾 Crear Backup", 
                  command=self.create_backup, bootstyle="warning").pack(side=tk.LEFT, padx=5)
        
        # Recent activity
        recent_frame = ttk.LabelFrame(main_container, text="Actividad Reciente", padding=15)
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Recent attendance list
        recent_columns = ("Nombre", "Hora", "Departamento", "Estado")
        self.recent_tree = ttk.Treeview(recent_frame, columns=recent_columns, show="headings", height=8)
        
        for col in recent_columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=150)
        
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=recent_scrollbar.set)
        
        self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load recent activity
        self.refresh_recent_activity()
    
    def create_stat_card(self, parent, title, value, icon):
        """Create a statistics card"""
        card = ttk.LabelFrame(parent, text=f"{icon} {title}", padding=15)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        value_label = ttk.Label(card, text=str(value), font=("Arial", 20, "bold"))
        value_label.pack()
    
    def create_registration_tab(self):
        """Enhanced registration tab"""
        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="👤 Registro")
        
        # Main container
        main_container = ttk.Frame(reg_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left side - Camera and registration
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Title
        title_label = ttk.Label(left_frame, text="Registro de Nuevo Usuario", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Camera selection
        camera_selection = ttk.Frame(left_frame)
        camera_selection.pack(fill=tk.X, pady=5)
        
        ttk.Label(camera_selection, text="Cámara:").pack(side=tk.LEFT)
        self.camera_combo = ttk.Combobox(camera_selection, state="readonly", width=10)
        self.camera_combo.pack(side=tk.LEFT, padx=5)
        self.camera_combo.bind("<<ComboboxSelected>>", self.on_camera_change)
        
        # Populate camera options
        available_cameras = self.face_system.get_available_cameras()
        self.camera_combo['values'] = [f"Cámara {i}" for i in available_cameras]
        if available_cameras:
            self.camera_combo.current(0)
        
        # Camera display
        self.camera_label = ttk.Label(left_frame, text="Cámara no disponible", 
                                     background="black", foreground="white")
        self.camera_label.pack(pady=10)
        
        # Camera controls
        camera_controls = ttk.Frame(left_frame)
        camera_controls.pack(pady=10)
        
        self.start_camera_btn = ttk.Button(camera_controls, text="📷 Iniciar Cámara", 
                                          command=self.start_camera, bootstyle="success")
        self.start_camera_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_camera_btn = ttk.Button(camera_controls, text="⏹ Detener Cámara", 
                                         command=self.stop_camera, bootstyle="danger")
        self.stop_camera_btn.pack(side=tk.LEFT, padx=5)
        
        # Enhanced registration form
        form_frame = ttk.LabelFrame(left_frame, text="Información del Usuario", padding=15)
        form_frame.pack(fill=tk.X, pady=20)
        
        # Name
        ttk.Label(form_frame, text="Nombre completo: *", font=("Arial", 12)).pack(anchor=tk.W)
        self.name_entry = ttk.Entry(form_frame, font=("Arial", 12))
        self.name_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Department
        ttk.Label(form_frame, text="Departamento:", font=("Arial", 12)).pack(anchor=tk.W)
        self.dept_entry = ttk.Entry(form_frame, font=("Arial", 12))
        self.dept_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Position
        ttk.Label(form_frame, text="Cargo/Posición:", font=("Arial", 12)).pack(anchor=tk.W)
        self.position_entry = ttk.Entry(form_frame, font=("Arial", 12))
        self.position_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Email
        ttk.Label(form_frame, text="Email:", font=("Arial", 12)).pack(anchor=tk.W)
        self.email_entry = ttk.Entry(form_frame, font=("Arial", 12))
        self.email_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Registration buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.register_btn = ttk.Button(btn_frame, text="✅ Registrar Usuario", 
                                      command=self.register_user, bootstyle="primary")
        self.register_btn.pack(side=tk.LEFT, padx=5)
        
        self.add_face_btn = ttk.Button(btn_frame, text="➕ Agregar Rostro", 
                                      command=self.add_additional_face, bootstyle="secondary")
        self.add_face_btn.pack(side=tk.LEFT, padx=5)
        
        self.reg_result_label = ttk.Label(form_frame, text="", font=("Arial", 10))
        self.reg_result_label.pack(pady=10)
        
        # Right side - Enhanced users list
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Users list with search
        users_frame = ttk.LabelFrame(right_frame, text="Usuarios Registrados", padding=15)
        users_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search box
        search_frame = ttk.Frame(users_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_users)
        
        # Enhanced columns
        columns = ("Nombre", "Código", "Departamento", "Asistencias", "Último")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        # Context menu for users
        self.create_user_context_menu()
        
        # Scrollbar
        users_scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        actions_frame = ttk.Frame(users_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(actions_frame, text="🔄 Actualizar", 
                  command=self.refresh_users_list, bootstyle="info").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🗑️ Eliminar Usuario", 
                  command=self.delete_selected_user, bootstyle="danger").pack(side=tk.LEFT, padx=5)
        
        # Load initial users list
        self.refresh_users_list()
    
    def create_user_context_menu(self):
        """Create context menu for user management"""
        self.user_context_menu = tk.Menu(self.root, tearoff=0)
        self.user_context_menu.add_command(label="Ver Detalles", command=self.view_user_details)
        self.user_context_menu.add_command(label="Agregar Rostro", command=self.add_face_to_selected_user)
        self.user_context_menu.add_separator()
        self.user_context_menu.add_command(label="Eliminar Usuario", command=self.delete_selected_user)
        
        self.users_tree.bind("<Button-3>", self.show_user_context_menu)
    
    def show_user_context_menu(self, event):
        """Show context menu for user management"""
        if self.users_tree.selection():
            self.user_context_menu.post(event.x_root, event.y_root)

    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        try:
            stats = self.face_system.get_attendance_statistics()
            # Update stats labels
            if hasattr(self, 'total_users_label'):
                self.total_users_label.config(text=str(stats['total_users']))
            if hasattr(self, 'today_attendance_label'):
                self.today_attendance_label.config(text=str(stats['today_attendance']))
            if hasattr(self, 'week_attendance_label'):
                self.week_attendance_label.config(text=str(stats['this_week_attendance']))
            if hasattr(self, 'month_attendance_label'):
                self.month_attendance_label.config(text=str(stats['this_month_attendance']))
                
        except Exception as e:
            print(f"Error updating dashboard stats: {e}")

    def load_recent_attendance(self):
        """Load recent attendance records"""
        try:
            # Clear existing items
            if hasattr(self, 'recent_tree'):
                for item in self.recent_tree.get_children():
                    self.recent_tree.delete(item)
                
                # Get recent records (last 10)
                recent_records = sorted(self.face_system.attendance_records, 
                                      key=lambda x: x['timestamp'], reverse=True)[:10]
                
                for record in recent_records:
                    user_info = self.face_system.registered_users.get(record['name'], {})
                    department = user_info.get('department', 'N/A')
                    
                    time_obj = datetime.strptime(record['timestamp'], "%Y-%m-%d %H:%M:%S")
                    time_str = time_obj.strftime("%H:%M")
                    
                    self.recent_tree.insert("", "end", values=(
                        record['name'],
                        time_str,
                        department,
                        record.get('type', 'Present')
                    ))
        except Exception as e:
            print(f"Error loading recent attendance: {e}")

    def refresh_recent_activity(self):
        """Refresh recent activity - alias for load_recent_attendance"""
        self.load_recent_attendance()

    def quick_recognition(self):
        """Start quick face recognition"""
        def recognition_thread():
            try:
                self.recognition_active = True
                self.start_camera_display()
            except Exception as e:
                messagebox.showerror("Error", f"Error al iniciar reconocimiento: {e}")
        
        threading.Thread(target=recognition_thread, daemon=True).start()

    def export_today(self):
        """Export today's attendance records"""
        try:
            today = datetime.now().date()
            success, message = self.face_system.export_to_excel(start_date=today, end_date=today)
            if success:
                messagebox.showinfo("Éxito", "Reporte de hoy exportado exitosamente")
            else:
                messagebox.showwarning("Advertencia", message)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")

    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        try:
            self.update_dashboard_stats()
            self.load_recent_attendance()
            messagebox.showinfo("Actualizado", "Dashboard actualizado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar dashboard: {e}")

    def create_backup(self):
        """Create backup of all data"""
        try:
            success = self.face_system.create_backup()
            if success:
                messagebox.showinfo("Éxito", "Backup creado exitosamente")
            else:
                messagebox.showerror("Error", "Error al crear backup")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear backup: {e}")

    def start_camera_display(self):
        """Start camera display for recognition"""
        if not hasattr(self, 'camera_window') or not self.camera_window.winfo_exists():
            self.camera_window = ttk.Toplevel(self.root)
            self.camera_window.title("Reconocimiento Facial - AsistoYA")
            self.camera_window.geometry("800x600")
            
            # Camera display
            self.camera_label = ttk.Label(self.camera_window)
            self.camera_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            
            # Control buttons
            controls_frame = ttk.Frame(self.camera_window)
            controls_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(controls_frame, text="Detener", 
                      command=self.stop_camera_display, bootstyle="danger").pack(side=tk.LEFT, padx=5)
            
            self.update_camera_display()

    def stop_camera_display(self):
        """Stop camera display"""
        self.recognition_active = False
        if hasattr(self, 'camera_window') and self.camera_window.winfo_exists():
            self.camera_window.destroy()

    def update_camera_display(self):
        """Update camera display with face recognition"""
        if not hasattr(self, 'recognition_active') or not self.recognition_active:
            return
            
        if hasattr(self, 'camera_window') and self.camera_window.winfo_exists():
            try:
                ret, frame = self.face_system.camera.read()
                if ret:
                    # Detect faces
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_system.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        # Draw rectangle around face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        
                        # Extract and recognize face
                        face_img = gray[y:y+h, x:x+w]
                        if face_img.size > 0:
                            name = self.face_system.recognize_face(face_img)
                            if name != "Unknown":
                                # Mark attendance
                                self.face_system.mark_attendance(name)
                                cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                            else:
                                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                    
                    # Convert to PhotoImage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((640, 480), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    self.camera_label.configure(image=photo)
                    self.camera_label.image = photo
                
                # Schedule next update
                self.camera_window.after(30, self.update_camera_display)
                
            except Exception as e:                print(f"Camera display error: {e}")

    def on_camera_change(self, event=None):
        """Handle camera selection change"""
        try:
            if hasattr(self, 'camera_combo'):
                selected = self.camera_combo.get()
                if selected and selected.startswith("Camera"):
                    camera_index = int(selected.split()[1])
                    self.face_system.change_camera(camera_index)
        except Exception as e:
            print(f"Error changing camera: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = AdvancedAttendanceApp(root)
    root.mainloop()