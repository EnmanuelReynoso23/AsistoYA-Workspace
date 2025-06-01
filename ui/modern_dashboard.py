"""
🏢 Dashboard Profesional Moderno - AsistoYA Empresarial
Interfaz avanzada con métricas en tiempo real
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
from typing import Dict, List, Optional

class ModernDashboard:
    def create_camera_panel(self):
        """Crear panel de visualización y control de cámara"""
        import cv2
        from PIL import Image, ImageTk
        camera_frame = ttk_bootstrap.LabelFrame(self.main_frame, text="Cámara en Vivo", bootstyle=INFO)
        camera_frame.pack(fill=X, pady=(0, 10))

        # Selector de cámara
        cameras = self.face_system.camera_manager.get_available_cameras()
        self.selected_camera = tk.IntVar(value=cameras[0] if cameras else 0)
        ttk_bootstrap.Label(camera_frame, text="Seleccionar cámara:").pack(side=LEFT, padx=5)
        self.camera_menu = ttk_bootstrap.Combobox(camera_frame, values=cameras, textvariable=self.selected_camera, width=5, state="readonly")
        self.camera_menu.pack(side=LEFT, padx=5)
        self.camera_menu.bind("<<ComboboxSelected>>", self.on_camera_selected)

        # Botón para iniciar/detener cámara
        self.camera_running = False
        self.camera_btn = ttk_bootstrap.Button(camera_frame, text="Iniciar Cámara", bootstyle=SUCCESS, command=self.toggle_camera)
        self.camera_btn.pack(side=LEFT, padx=5)

        # Widget para mostrar la imagen
        self.camera_label = ttk_bootstrap.Label(camera_frame)
        self.camera_label.pack(side=LEFT, padx=10)

    def on_camera_selected(self, event=None):
        idx = self.selected_camera.get()
        self.face_system.camera_manager.switch_camera(idx)

    def toggle_camera(self):
        if not self.camera_running:
            if self.face_system.camera_manager.start_capture():
                self.camera_running = True
                self.camera_btn.config(text="Detener Cámara", bootstyle=DANGER)
                self.update_camera_frame()
            else:
                messagebox.showerror("Cámara", "No se pudo iniciar la cámara seleccionada.")
        else:
            self.face_system.camera_manager.stop_capture()
            self.camera_running = False
            self.camera_btn.config(text="Iniciar Cámara", bootstyle=SUCCESS)
            self.camera_label.config(image="")

    def update_camera_frame(self):
        if self.camera_running:
            frame = self.face_system.camera_manager.get_frame()
            if frame is not None:
                import cv2
                from PIL import Image, ImageTk
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img.resize((320, 240)))
                self.camera_label.imgtk = imgtk
                self.camera_label.config(image=imgtk)
            self.parent.after(30, self.update_camera_frame)
    """Dashboard empresarial moderno con métricas avanzadas"""
    
    def __init__(self, parent, auth_manager, firebase_config):
        self.parent = parent
        self.auth_manager = auth_manager
        self.firebase = firebase_config
        self.current_user = None
        self.current_token = None
        # Integración real de reconocimiento facial
        from face_recognition.recognition_system import FaceRecognitionSystem
        self.face_system = FaceRecognitionSystem()
        
        # Configurar tema moderno
        self.style = ttk_bootstrap.Style(theme="superhero")  # Tema oscuro profesional
        
        # Variables de estado
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = 30000  # 30 segundos
        
        # Métricas en tiempo real
        self.metrics = {
            'total_students': tk.StringVar(value="0"),
            'present_today': tk.StringVar(value="0"),
            'absent_today': tk.StringVar(value="0"),
            'attendance_rate': tk.StringVar(value="0%"),
            'last_recognition': tk.StringVar(value="Ninguno"),
            'active_cameras': tk.StringVar(value="1")
        }
        
        self.setup_dashboard()
        self.start_auto_refresh()
    
    def setup_dashboard(self):
        """Configurar dashboard principal"""
        # Frame principal
        self.main_frame = ttk_bootstrap.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Header con información del usuario
        self.create_header()
        
        # Panel de métricas principales
        self.create_metrics_panel()
        
        # Panel de gráficos
        self.create_charts_panel()
        
        # Panel de actividad reciente
        self.create_activity_panel()
        
        # Panel de acciones rápidas
        self.create_quick_actions()
        # Panel de cámara
        self.create_camera_panel()
        # Barra de estado
        self.create_status_bar()
    
    def create_header(self):
        """Crear header del dashboard"""
        header_frame = ttk_bootstrap.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Logo y título
        title_frame = ttk_bootstrap.Frame(header_frame)
        title_frame.pack(side=LEFT)
        
        title_label = ttk_bootstrap.Label(
            title_frame,
            text="🏢 AsistoYA Dashboard Empresarial",
            font=("Segoe UI", 24, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(anchor=W)
        
        subtitle_label = ttk_bootstrap.Label(
            title_frame,
            text=f"Sistema de Control de Asistencia Avanzado",
            font=("Segoe UI", 12),
            bootstyle=SECONDARY
        )
        subtitle_label.pack(anchor=W)
        
        # Panel de usuario
        user_frame = ttk_bootstrap.Frame(header_frame)
        user_frame.pack(side=RIGHT)
        
        # Info del usuario (se actualizará después del login)
        self.user_info_label = ttk_bootstrap.Label(
            user_frame,
            text="👤 Usuario no autenticado",
            font=("Segoe UI", 10),
            bootstyle=INFO
        )
        self.user_info_label.pack(anchor=E)
        
        # Hora actual
        self.time_label = ttk_bootstrap.Label(
            user_frame,
            text="",
            font=("Segoe UI", 10),
            bootstyle=SECONDARY
        )
        self.time_label.pack(anchor=E)
        
        self.update_time()
    
    def create_metrics_panel(self):
        """Crear panel de métricas principales"""
        metrics_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="📊 Métricas en Tiempo Real",
            bootstyle=PRIMARY
        )
        metrics_frame.pack(fill=X, pady=(0, 10))
        
        # Grid de métricas
        metrics_grid = ttk_bootstrap.Frame(metrics_frame)
        metrics_grid.pack(fill=X, padx=10, pady=10)
        
        # Configurar grid
        for i in range(6):
            metrics_grid.columnconfigure(i, weight=1)
        
        # Métricas individuales
        self.create_metric_card(metrics_grid, "👥 Total Estudiantes", 
                               self.metrics['total_students'], SUCCESS, 0, 0)
        
        self.create_metric_card(metrics_grid, "✅ Presentes Hoy", 
                               self.metrics['present_today'], PRIMARY, 0, 1)
        
        self.create_metric_card(metrics_grid, "❌ Ausentes Hoy", 
                               self.metrics['absent_today'], DANGER, 0, 2)
        
        self.create_metric_card(metrics_grid, "📈 Tasa de Asistencia", 
                               self.metrics['attendance_rate'], INFO, 0, 3)
        
        self.create_metric_card(metrics_grid, "🎯 Último Reconocimiento", 
                               self.metrics['last_recognition'], WARNING, 0, 4)
        
        self.create_metric_card(metrics_grid, "📹 Cámaras Activas", 
                               self.metrics['active_cameras'], SECONDARY, 0, 5)
    
    def create_metric_card(self, parent, title, variable, style, row, col):
        """Crear tarjeta de métrica individual"""
        card = ttk_bootstrap.Frame(parent, bootstyle=style)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        title_label = ttk_bootstrap.Label(
            card,
            text=title,
            font=("Segoe UI", 9, "bold"),
            bootstyle=f"{style}-inverse"
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ttk_bootstrap.Label(
            card,
            textvariable=variable,
            font=("Segoe UI", 16, "bold"),
            bootstyle=f"{style}-inverse"
        )
        value_label.pack(pady=(0, 10))
    
    def create_charts_panel(self):
        """Crear panel de gráficos"""
        charts_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="📈 Análisis Visual",
            bootstyle=INFO
        )
        charts_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Notebook para múltiples gráficos
        chart_notebook = ttk_bootstrap.Notebook(charts_frame)
        chart_notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Gráfico de asistencia semanal
        self.create_attendance_chart(chart_notebook)
        
        # Gráfico de tendencias
        self.create_trends_chart(chart_notebook)
        
        # Gráfico de distribución por horas
        self.create_hourly_chart(chart_notebook)
    
    def create_attendance_chart(self, parent):
        """Crear gráfico de asistencia semanal"""
        frame = ttk_bootstrap.Frame(parent)
        parent.add(frame, text="Asistencia Semanal")
        
        # Crear figura matplotlib
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b3e50')  # Fondo oscuro
        ax.set_facecolor('#34495e')
        
        # Datos de ejemplo (se actualizarán con datos reales)
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        attendance = [85, 92, 78, 95, 88, 45, 23]
        
        bars = ax.bar(days, attendance, color='#3498db', alpha=0.8)
        ax.set_ylabel('Porcentaje de Asistencia', color='white')
        ax.set_title('Asistencia por Día de la Semana', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        
        # Personalizar apariencia
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height}%', ha='center', va='bottom', color='white')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def create_trends_chart(self, parent):
        """Crear gráfico de tendencias mensuales"""
        frame = ttk_bootstrap.Frame(parent)
        parent.add(frame, text="Tendencias Mensuales")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#34495e')
        
        # Datos de ejemplo
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        attendance_trend = [82, 85, 88, 92, 89, 91]
        
        ax.plot(months, attendance_trend, marker='o', linewidth=3, 
                markersize=8, color='#e74c3c')
        ax.fill_between(months, attendance_trend, alpha=0.3, color='#e74c3c')
        
        ax.set_ylabel('Asistencia Promedio (%)', color='white')
        ax.set_title('Tendencia de Asistencia Mensual', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        
        # Personalizar apariencia
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def create_hourly_chart(self, parent):
        """Crear gráfico de distribución por horas"""
        frame = ttk_bootstrap.Frame(parent)
        parent.add(frame, text="Distribución Horaria")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#34495e')
        
        # Datos de ejemplo
        hours = ['7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00']
        arrivals = [5, 15, 45, 25, 8, 3, 1]
        
        ax.bar(hours, arrivals, color='#f39c12', alpha=0.8)
        ax.set_ylabel('Número de Llegadas', color='white')
        ax.set_title('Distribución de Llegadas por Hora', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        
        # Personalizar apariencia
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def create_activity_panel(self):
        """Crear panel de actividad reciente"""
        activity_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="🕐 Actividad Reciente",
            bootstyle=WARNING
        )
        activity_frame.pack(fill=X, pady=(0, 10))
        
        # Crear Treeview para actividad
        columns = ("Hora", "Estudiante", "Acción", "Estado")
        self.activity_tree = ttk_bootstrap.Treeview(
            activity_frame,
            columns=columns,
            show="headings",
            height=6,
            bootstyle=WARNING
        )
        
        # Configurar columnas
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk_bootstrap.Scrollbar(
            activity_frame,
            orient=VERTICAL,
            command=self.activity_tree.yview
        )
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.activity_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=RIGHT, fill=Y, pady=10)
        
        # Agregar datos de ejemplo
        self.update_activity_log()
    
    def create_quick_actions(self):
        """Crear panel de acciones rápidas"""
        actions_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="⚡ Acciones Rápidas",
            bootstyle=SUCCESS
        )
        actions_frame.pack(fill=X, pady=(0, 10))
        
        buttons_frame = ttk_bootstrap.Frame(actions_frame)
        buttons_frame.pack(fill=X, padx=10, pady=10)
          # Botones principales funcionales
        ttk_bootstrap.Button(
            buttons_frame,
            text="Registrar Usuario/Rostro",
            bootstyle=PRIMARY,
            width=22,
            command=self.register_face
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="Iniciar Reconocimiento",
            bootstyle=SUCCESS,
            width=22,
            command=self.start_recognition
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="Enviar Notificaciones",
            bootstyle=WARNING,
            width=22,
            command=self.send_notifications
        ).pack(side=LEFT, padx=5)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_frame = ttk_bootstrap.Frame(self.main_frame, bootstyle=DARK)
        status_frame.pack(fill=X, side=BOTTOM)
        
        # Estado de sistemas
        self.firebase_status = ttk_bootstrap.Label(
            status_frame,
            text="🔥 Firebase: Conectado",
            bootstyle=SUCCESS,
            font=("Segoe UI", 9)
        )
        self.firebase_status.pack(side=LEFT, padx=5, pady=2)
        
        self.camera_status = ttk_bootstrap.Label(
            status_frame,
            text="📹 Cámara: Lista",
            bootstyle=SUCCESS,
            font=("Segoe UI", 9)
        )
        self.camera_status.pack(side=LEFT, padx=5, pady=2)
        
        # Auto-refresh toggle
        refresh_frame = ttk_bootstrap.Frame(status_frame)
        refresh_frame.pack(side=RIGHT, padx=5, pady=2)
        
        ttk_bootstrap.Checkbutton(
            refresh_frame,
            text="Auto-refresh",
            variable=self.auto_refresh,
            bootstyle="round-toggle"
        ).pack(side=RIGHT)
    
    def update_time(self):
        """Actualizar hora en tiempo real"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"🕐 {current_time}")
        self.parent.after(1000, self.update_time)
    
    def start_auto_refresh(self):
        """Iniciar actualización automática"""
        if self.auto_refresh.get():
            self.refresh_metrics()
        self.parent.after(self.refresh_interval, self.start_auto_refresh)
    
    def refresh_metrics(self):
        """Actualizar métricas del dashboard"""
        try:
            # Aquí se conectaría con la base de datos real
            # Por ahora, datos simulados
            
            # Simular datos en tiempo real
            import random
            
            total_students = 150 + random.randint(-5, 5)
            present_today = int(total_students * (0.85 + random.uniform(-0.1, 0.1)))
            absent_today = total_students - present_today
            attendance_rate = (present_today / total_students) * 100
            
            # Actualizar variables
            self.metrics['total_students'].set(str(total_students))
            self.metrics['present_today'].set(str(present_today))
            self.metrics['absent_today'].set(str(absent_today))
            self.metrics['attendance_rate'].set(f"{attendance_rate:.1f}%")
            self.metrics['last_recognition'].set("Juan Pérez - 10:35 AM")
            
            # Actualizar actividad
            self.update_activity_log()
            
        except Exception as e:
            print(f"Error actualizando métricas: {e}")
    
    def update_activity_log(self):
        """Actualizar log de actividad"""
        # Limpiar actividad anterior
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Agregar actividad simulada
        activities = [
            ("10:35:22", "Juan Pérez", "Reconocimiento facial", "✅ Exitoso"),
            ("10:34:15", "María García", "Reconocimiento facial", "✅ Exitoso"),
            ("10:33:08", "Carlos López", "Reconocimiento facial", "❌ Fallido"),
            ("10:32:45", "Ana Martínez", "Reconocimiento facial", "✅ Exitoso"),
            ("10:31:20", "Pedro Sánchez", "Reconocimiento facial", "✅ Exitoso")
        ]
        
        for activity in activities:
            self.activity_tree.insert("", "end", values=activity)
    
    def set_user(self, user: Dict, token: str):
        """Establecer usuario autenticado"""
        self.current_user = user
        self.current_token = token
        
        user_text = f"👤 {user['full_name']} ({user['role'].title()})"
        self.user_info_label.config(text=user_text)
    
    # Métodos para acciones rápidas    def start_recognition(self):
        """Iniciar reconocimiento facial real"""
        try:
            # Crear ventana de reconocimiento en tiempo real
            recognition_window = tk.Toplevel(self.parent)
            recognition_window.title("Reconocimiento Facial en Tiempo Real")
            recognition_window.geometry("800x600")
            recognition_window.grab_set()
            
            # Frame principal
            main_frame = ttk_bootstrap.Frame(recognition_window, padding=20)
            main_frame.pack(fill=BOTH, expand=True)
            
            # Título
            title_label = ttk_bootstrap.Label(
                main_frame,
                text="Sistema de Reconocimiento Facial Activo",
                font=("Segoe UI", 16, "bold"),
                bootstyle=SUCCESS
            )
            title_label.pack(pady=(0, 20))
            
            # Frame para video
            video_frame = ttk_bootstrap.LabelFrame(main_frame, text="Video en Vivo", bootstyle=INFO)
            video_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
            
            # Label para mostrar video
            self.recognition_label = ttk_bootstrap.Label(video_frame)
            self.recognition_label.pack(pady=10)
            
            # Frame de información
            info_frame = ttk_bootstrap.Frame(main_frame)
            info_frame.pack(fill=X, pady=(0, 20))
            
            self.recognition_status = ttk_bootstrap.Label(
                info_frame,
                text="Estado: Iniciando...",
                font=("Segoe UI", 12),
                bootstyle=WARNING
            )
            self.recognition_status.pack()
            
            # Inicializar reconocimiento
            init_result = self.face_system.initialize()
            if not init_result['success']:
                messagebox.showerror("Error", f"Error inicializando: {', '.join(init_result['errors'])}")
                recognition_window.destroy()
                return
            
            # Iniciar reconocimiento
            if self.face_system.start_recognition():
                self.recognition_status.config(text="Estado: Reconocimiento activo", bootstyle=SUCCESS)
                self.recognition_active = True
                self.update_recognition_display(recognition_window)
            else:
                messagebox.showerror("Error", "No se pudo iniciar el reconocimiento")
                recognition_window.destroy()
                return
            
            # Botón para detener
            def stop_recognition():
                self.face_system.stop_recognition()
                self.recognition_active = False
                recognition_window.destroy()
            
            ttk_bootstrap.Button(
                main_frame,
                text="Detener Reconocimiento",
                bootstyle=DANGER,
                command=stop_recognition
            ).pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando reconocimiento: {str(e)}")
    
    def update_recognition_display(self, window):
        """Actualizar display de reconocimiento"""
        if hasattr(self, 'recognition_active') and self.recognition_active:
            frame = self.face_system.get_current_frame_with_detections()
            if frame is not None:
                import cv2
                from PIL import Image, ImageTk
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img.resize((640, 480)))
                self.recognition_label.imgtk = imgtk
                self.recognition_label.config(image=imgtk)
            
            # Programar siguiente actualización
            window.after(30, lambda: self.update_recognition_display(window))
    
    def export_report(self):
        """Exportar reporte (placeholder real)"""
        # Aquí deberías llamar a la función real de exportación de reportes
        messagebox.showinfo("Reporte", "Exportando reporte de asistencia...")
    
    def manage_students(self):
        """Gestionar estudiantes (placeholder real)"""
        # Aquí deberías llamar a la función real de gestión de estudiantes
        messagebox.showinfo("Estudiantes", "Abriendo gestión de estudiantes...")
    
    def send_notifications(self):
        """Enviar notificaciones (placeholder real)"""
        # Aquí deberías llamar a la función real de notificaciones
        messagebox.showinfo("Notificaciones", "Enviando notificaciones...")
    
    def open_settings(self):
        """Abrir configuración (placeholder real)"""
        # Aquí deberías llamar a la función real de configuración
        messagebox.showinfo("Configuración", "Abriendo configuración del sistema...")
    
    def register_face(self):
        """Registrar rostro de un nuevo estudiante"""
        try:
            # Crear ventana de registro
            register_window = tk.Toplevel(self.parent)
            register_window.title("Registrar Nuevo Estudiante")
            register_window.geometry("600x500")
            register_window.grab_set()
            
            # Frame principal
            main_frame = ttk_bootstrap.Frame(register_window, padding=20)
            main_frame.pack(fill=BOTH, expand=True)
            
            # Título
            title_label = ttk_bootstrap.Label(
                main_frame, 
                text="Registro de Nuevo Estudiante",
                font=("Segoe UI", 16, "bold"),
                bootstyle=PRIMARY
            )
            title_label.pack(pady=(0, 20))
            
            # Campos de información
            info_frame = ttk_bootstrap.Frame(main_frame)
            info_frame.pack(fill=X, pady=(0, 20))
            
            ttk_bootstrap.Label(info_frame, text="Nombre completo:").pack(anchor=W)
            name_entry = ttk_bootstrap.Entry(info_frame, width=50)
            name_entry.pack(fill=X, pady=(5, 10))
            
            ttk_bootstrap.Label(info_frame, text="ID del estudiante:").pack(anchor=W)
            id_entry = ttk_bootstrap.Entry(info_frame, width=50)
            id_entry.pack(fill=X, pady=(5, 10))
            
            ttk_bootstrap.Label(info_frame, text="Curso/Grado:").pack(anchor=W)
            course_entry = ttk_bootstrap.Entry(info_frame, width=50)
            course_entry.pack(fill=X, pady=(5, 10))
            
            # Frame para la cámara
            camera_frame = ttk_bootstrap.LabelFrame(main_frame, text="Captura de Rostro", bootstyle=INFO)
            camera_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
            
            # Label para mostrar la imagen
            self.capture_label = ttk_bootstrap.Label(camera_frame)
            self.capture_label.pack(pady=10)
            
            # Botones de acción
            action_frame = ttk_bootstrap.Frame(main_frame)
            action_frame.pack(fill=X)
            
            def capture_photo():
                """Capturar foto del estudiante"""
                if not self.face_system.camera_manager.camera_available:
                    if not self.face_system.camera_manager.initialize_camera():
                        messagebox.showerror("Error", "No se pudo acceder a la cámara")
                        return
                
                # Capturar frame
                frame = self.face_system.camera_manager.capture_single_frame()
                if frame is not None:
                    # Mostrar imagen capturada
                    import cv2
                    from PIL import Image, ImageTk
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    imgtk = ImageTk.PhotoImage(image=img.resize((300, 225)))
                    self.capture_label.imgtk = imgtk
                    self.capture_label.config(image=imgtk)
                    
                    # Guardar frame para registro
                    self.captured_frame = frame
                    messagebox.showinfo("Éxito", "Foto capturada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo capturar la foto")
            
            def save_student():
                """Guardar estudiante con rostro"""
                name = name_entry.get().strip()
                student_id = id_entry.get().strip()
                course = course_entry.get().strip()
                
                if not name or not student_id:
                    messagebox.showerror("Error", "Nombre e ID son obligatorios")
                    return
                
                if not hasattr(self, 'captured_frame'):
                    messagebox.showerror("Error", "Debe capturar una foto primero")
                    return
                
                try:
                    # Entrenar el reconocedor con la nueva cara
                    success = self.face_system.face_recognizer.add_person(
                        name=name,
                        student_id=student_id,
                        face_image=self.captured_frame
                    )
                    
                    if success:
                        messagebox.showinfo("Éxito", f"Estudiante {name} registrado correctamente")
                        register_window.destroy()
                    else:
                        messagebox.showerror("Error", "No se pudo registrar el rostro")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error registrando estudiante: {str(e)}")
            
            ttk_bootstrap.Button(
                action_frame,
                text="Capturar Foto",
                bootstyle=INFO,
                command=capture_photo
            ).pack(side=LEFT, padx=5)
            
            ttk_bootstrap.Button(
                action_frame,
                text="Guardar Estudiante",
                bootstyle=SUCCESS,
                command=save_student
            ).pack(side=LEFT, padx=5)
            
            ttk_bootstrap.Button(
                action_frame,
                text="Cancelar",
                bootstyle=SECONDARY,
                command=register_window.destroy
            ).pack(side=RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo registro: {str(e)}")
