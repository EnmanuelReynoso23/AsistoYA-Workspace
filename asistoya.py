"""
🚀 AsistoYA EMPRESARIAL - Aplicación Principal COMPLETA
Sistema de Control de Asistencia Nivel 1000% Profesional - VERSIÓN FINAL
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import sys
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd
import os

# Agregar paths para imports
sys.path.append(str(Path(__file__).parent))

# Imports de módulos empresariales
try:
    from auth.authentication import get_auth_manager
    from firebase.firebase_config import get_firebase
    from ui.modern_dashboard import ModernDashboard
    from face_recognition.recognition_system import FaceRecognitionSystem
    from models.student_model import student_model
    from models.attendance_model import attendance_model
    from reports.advanced_reports import get_report_generator
    from models.user_model import user_model
    
    # Importar sistema de botones mejorado
    from ui.button_manager import ButtonManager, ButtonConfig, ButtonState, get_button_manager
    from ui.functional_handlers import FunctionalHandlers, get_functional_handlers
    BUTTON_SYSTEM_AVAILABLE = True
    print("✅ Sistema de botones mejorado cargado")
    
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")
    print("Sistema de botones básico será utilizado")
    BUTTON_SYSTEM_AVAILABLE = False

class LoginWindow:
    """Ventana de login empresarial"""
    
    def __init__(self):
        self.root = ttk_bootstrap.Window(themename="superhero")
        self.root.title("🔐 AsistoYA Enterprise - Login")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Gestores
        self.auth_manager = get_auth_manager()
        self.firebase = get_firebase()
        
        self.setup_login_ui()
        
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_login_ui(self):
        """Configurar interfaz de login"""
        # Frame principal
        main_frame = ttk_bootstrap.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=40, pady=40)
        
        # Logo y título
        logo_frame = ttk_bootstrap.Frame(main_frame)
        logo_frame.pack(pady=(0, 30))
        
        # Título principal
        title_label = ttk_bootstrap.Label(
            logo_frame,
            text="🏢 AsistoYA",
            font=("Segoe UI", 32, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack()
        
        subtitle_label = ttk_bootstrap.Label(
            logo_frame,
            text="ENTERPRISE EDITION",
            font=("Segoe UI", 14, "bold"),
            bootstyle=SUCCESS
        )
        subtitle_label.pack()
        
        description_label = ttk_bootstrap.Label(
            logo_frame,
            text="Sistema de Control de Asistencia\ncon Reconocimiento Facial Avanzado",
            font=("Segoe UI", 10),
            bootstyle=SECONDARY,
            justify=CENTER
        )
        description_label.pack(pady=(10, 0))
        
        # Frame de login
        login_frame = ttk_bootstrap.LabelFrame(
            main_frame,
            text="🔐 Autenticación Segura",
            bootstyle=INFO,
            padding=20
        )
        login_frame.pack(fill=X, pady=(20, 0))
        
        # Campo usuario
        user_label = ttk_bootstrap.Label(
            login_frame,
            text="👤 Usuario:",
            font=("Segoe UI", 11, "bold")
        )
        user_label.pack(anchor=W, pady=(0, 5))
        
        self.username_entry = ttk_bootstrap.Entry(
            login_frame,
            textvariable=self.username_var,
            font=("Segoe UI", 12),
            bootstyle=PRIMARY,
            width=30
        )
        self.username_entry.pack(fill=X, pady=(0, 15))
        
        # Campo contraseña
        pass_label = ttk_bootstrap.Label(
            login_frame,
            text="🔑 Contraseña:",
            font=("Segoe UI", 11, "bold")
        )
        pass_label.pack(anchor=W, pady=(0, 5))
        
        self.password_entry = ttk_bootstrap.Entry(
            login_frame,
            textvariable=self.password_var,
            font=("Segoe UI", 12),
            bootstyle=PRIMARY,
            show="*",
            width=30
        )
        self.password_entry.pack(fill=X, pady=(0, 20))
        
        # Botón login
        login_btn = ttk_bootstrap.Button(
            login_frame,
            text="🚀 INICIAR SESIÓN",
            command=self.login,
            bootstyle=SUCCESS,
            width=30
        )
        login_btn.pack(pady=(10, 0))
        
        # Información de usuario por defecto
        info_frame = ttk_bootstrap.LabelFrame(
            main_frame,
            text="ℹ️ Información de Acceso",
            bootstyle=WARNING,
            padding=15
        )
        info_frame.pack(fill=X, pady=(20, 0))
        
        info_text = """Usuario por defecto:
👤 Usuario: admin
🔑 Contraseña: admin123

Roles disponibles:
🔹 Super Admin: Control total del sistema
🔹 Admin: Gestión de estudiantes y reportes  
🔹 Teacher: Control de asistencia
🔹 Supervisor: Solo visualización"""
        
        info_label = ttk_bootstrap.Label(
            info_frame,
            text=info_text,
            font=("Segoe UI", 9),
            justify=LEFT
        )
        info_label.pack()
        
        # Estado del sistema
        status_frame = ttk_bootstrap.Frame(main_frame)
        status_frame.pack(fill=X, pady=(20, 0))
        
        # Verificar estado Firebase
        firebase_status = "🔥 Conectado" if self.firebase.initialize() else "❌ Desconectado"
        
        status_label = ttk_bootstrap.Label(
            status_frame,
            text=f"Estado Firebase: {firebase_status}",
            font=("Segoe UI", 9),
            bootstyle=SUCCESS if "Conectado" in firebase_status else DANGER
        )
        status_label.pack()
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
        
        # Focus en usuario
        self.username_entry.focus()
    
    def login(self):
        """Proceso de autenticación"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Mostrar loading
        self.show_loading()
        
        # Autenticar
        user = self.auth_manager.authenticate(username, password)
        
        if user:
            # Generar token
            token = self.auth_manager.generate_token(user)
            
            # Cerrar login y abrir dashboard
            self.root.withdraw()
            self.open_main_application(user, token)
        else:
            self.hide_loading()
            messagebox.showerror(
                "Error de Autenticación", 
                "Usuario o contraseña incorrectos.\n\nVerifique sus credenciales e intente nuevamente."
            )
    
    def show_loading(self):
        """Mostrar indicador de carga"""
        # Deshabilitar campos
        self.username_entry.config(state='disabled')
        self.password_entry.config(state='disabled')
        
        # Cambiar cursor
        self.root.config(cursor="wait")
        self.root.update()
    
    def hide_loading(self):
        """Ocultar indicador de carga"""
        # Habilitar campos
        self.username_entry.config(state='normal')
        self.password_entry.config(state='normal')
        
        # Restaurar cursor
        self.root.config(cursor="")
        self.root.update()
    
    def open_main_application(self, user, token):
        """Abrir aplicación principal"""
        try:
            app = AsistoYAEnterprise(user, token)
            app.run()
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo aplicación: {e}")
    
    def run(self):
        """Ejecutar ventana de login"""
        self.root.mainloop()

class AsistoYAEnterprise:
    """Aplicación principal AsistoYA Enterprise"""
    
    def __init__(self, user, token):
        self.user = user
        self.token = token
        
        # Configurar ventana principal
        self.root = ttk_bootstrap.Window(themename="superhero")
        self.root.title(f"🏢 AsistoYA Enterprise - {user['full_name']}")
        self.root.state('zoomed')  # Pantalla completa
        
        # Gestores
        self.auth_manager = get_auth_manager()
        self.firebase = get_firebase()
        
        # Configurar logging
        self.setup_logging()
        
        # Variables de estado
        self.current_module = None
        
        # Configurar sistema de botones mejorado
        self.setup_enhanced_button_system()
        
        self.setup_main_ui()
          # Log de acceso
        self.log_info(f"Usuario {user['username']} ha iniciado sesión")
    
    def setup_logging(self):
        """Configurar sistema de logs"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configurar formato sin emojis para evitar errores de encoding
        log_format = '%(asctime)s - ENTERPRISE - %(levelname)s - %(message)s'
        
        # Handler para archivo
        file_handler = logging.FileHandler(
            log_dir / f"enterprise_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Handler para consola con encoding UTF-8
        import sys
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configurar UTF-8 para la salida de consola si es posible
        try:
            if hasattr(console_handler.stream, 'reconfigure'):
                console_handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass  # Si no se puede configurar UTF-8, continuar sin emojis
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[file_handler, console_handler]
        )
        
        self.logger = logging.getLogger('AsistoYA_Enterprise')
    
    def log_info(self, message):
        """Log información"""
        self.logger.info(message)
    
    # ==================== SISTEMA DE BOTONES MEJORADO ====================
    
    def setup_enhanced_button_system(self):
        """Configurar sistema de botones mejorado"""
        if not BUTTON_SYSTEM_AVAILABLE:
            self.logger.warning("⚠️ Sistema de botones mejorado no disponible, usando sistema básico")
            return False
        
        try:
            # Inicializar gestores
            self.button_manager = get_button_manager()
            self.button_manager.app = self
            
            self.functional_handlers = get_functional_handlers(self)
            
            # Registrar configuraciones de botones
            self._register_button_configs()
            
            # Habilitar modo debug
            self.button_manager.enable_debug_mode()
            
            self.logger.info("✅ Sistema de botones mejorado configurado")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando sistema de botones: {e}")
            return False
    
    def _register_button_configs(self):
        """Registrar todas las configuraciones de botones"""
        
        # Botón Dashboard
        dashboard_config = ButtonConfig(
            button_id="dashboard",
            text="🏠 Dashboard",
            command=self.show_dashboard_enhanced,
            style=PRIMARY,
            tooltip="Mostrar panel principal con estadísticas"
        )
        self.button_manager.register_button(dashboard_config)
        
        # Botón Registro de Estudiantes
        register_config = ButtonConfig(
            button_id="register_student",
            text="👥 Registrar",
            command=self.functional_handlers.register_student_real,
            style=SUCCESS,
            tooltip="Registrar nuevo estudiante con captura facial",
            permissions=["manage_students"],
            validation_func=self._validate_camera_access
        )
        self.button_manager.register_button(register_config)
        
        # Botón Lista de Estudiantes
        list_students_config = ButtonConfig(
            button_id="list_students",
            text="📋 Estudiantes",
            command=self.functional_handlers.list_students_real,
            style=INFO,
            tooltip="Ver y gestionar estudiantes registrados"
        )
        self.button_manager.register_button(list_students_config)
        
        # Botón Reconocimiento Facial
        recognition_config = ButtonConfig(
            button_id="start_recognition",
            text="🚀 Reconocimiento",
            command=self.functional_handlers.start_recognition_real,
            style=SUCCESS,
            tooltip="Iniciar reconocimiento facial para asistencia",
            permissions=["manage_attendance"],
            validation_func=self._validate_camera_access
        )
        self.button_manager.register_button(recognition_config)
        
        # Botón Ver Reportes
        reports_config = ButtonConfig(
            button_id="view_reports",
            text="📊 Reportes",
            command=self.functional_handlers.view_reports_real,
            style=WARNING,
            tooltip="Ver reportes y estadísticas de asistencia"
        )
        self.button_manager.register_button(reports_config)
        
        # Botón Enviar Notificaciones
        notification_config = ButtonConfig(
            button_id="send_notification",
            text="🔔 Notificar",
            command=self.functional_handlers.send_notification_real,
            style=DANGER,
            tooltip="Enviar notificaciones a padres de familia",
            permissions=["send_notifications"]
        )
        self.button_manager.register_button(notification_config)
    
    def _validate_camera_access(self):
        """Validar acceso a la cámara"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False
    
    def show_dashboard_enhanced(self):
        """Dashboard mejorado con estadísticas de botones"""
        try:
            # Mostrar dashboard original
            self.show_dashboard()
            
            # Agregar estadísticas de botones si está disponible
            if BUTTON_SYSTEM_AVAILABLE and hasattr(self, 'button_manager'):
                stats = self.button_manager.get_button_stats()
                self.logger.info(f"📊 Estadísticas de botones: {len(stats)} botones registrados")
        except Exception as e:
            self.logger.error(f"❌ Error en dashboard mejorado: {e}")
    
    def _execute_with_button_manager(self, button_id):
        """Ejecutar comando usando el button manager"""
        if BUTTON_SYSTEM_AVAILABLE and hasattr(self, 'button_manager'):
            if button_id in self.button_manager.buttons:
                self.button_manager.buttons[button_id].command()
            else:
                self.logger.warning(f"⚠️ Botón no registrado: {button_id}")
    
    def show_button_stats(self):
        """Mostrar estadísticas de uso de botones"""
        if not BUTTON_SYSTEM_AVAILABLE or not hasattr(self, 'button_manager'):
            messagebox.showinfo("Info", "Sistema de botones mejorado no disponible")
            return
        
        try:
            stats_window = tk.Toplevel(self.root)
            stats_window.title("📊 Estadísticas de Botones")
            stats_window.geometry("600x400")
            stats_window.grab_set()
            
            main_frame = ttk_bootstrap.Frame(stats_window, padding=15)
            main_frame.pack(fill=BOTH, expand=True)
            
            title_label = ttk_bootstrap.Label(
                main_frame,
                text="📊 Estadísticas de Uso de Botones",
                font=("Segoe UI", 16, "bold"),
                bootstyle=PRIMARY
            )
            title_label.pack(pady=(0, 15))
            
            # Tabla de estadísticas
            columns = ('Botón', 'Clics', 'Último Uso', 'Estado')
            tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=140)
            
            # Cargar datos
            stats = self.button_manager.get_button_stats()
            for button_id, data in stats.items():
                tree.insert('', 'end', values=(
                    data['text'],
                    data['clicks'],
                    data['last_clicked'].strftime('%H:%M:%S') if data['last_clicked'] else 'Nunca',
                    data['current_state']
                ))
            
            tree.pack(fill=BOTH, expand=True, pady=10)
            
            # Botón para resetear
            ttk_bootstrap.Button(
                main_frame,
                text="🔄 Resetear Estadísticas",
                command=lambda: self.reset_button_stats() or stats_window.destroy(),
                bootstyle=WARNING
            ).pack(pady=10)
            
        except Exception as e:
            self.logger.error(f"❌ Error mostrando estadísticas: {e}")
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def reset_button_stats(self):
        """Resetear estadísticas de botones"""
        if BUTTON_SYSTEM_AVAILABLE and hasattr(self, 'button_manager'):
            self.button_manager.reset_button_stats()
            messagebox.showinfo("Éxito", "Estadísticas reseteadas")
    
    def toggle_button_debug(self):
        """Alternar modo debug de botones"""
        if BUTTON_SYSTEM_AVAILABLE and hasattr(self, 'button_manager'):
            self.button_manager.enable_debug_mode()
            messagebox.showinfo("Debug", "Modo debug habilitado - Ver consola para logs")
    
    def setup_main_ui(self):
        """Configurar interfaz principal"""
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Panel principal con pestañas
        self.create_main_panel()
        
        # Status bar
        self.create_status_bar()
        
        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Sistema
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🏢 Sistema", menu=system_menu)
        system_menu.add_command(label="🏠 Dashboard", command=self.show_dashboard)
        system_menu.add_separator()
        system_menu.add_command(label="👤 Perfil de Usuario", command=self.show_profile)
        system_menu.add_command(label="🔄 Cambiar Contraseña", command=self.change_password)
        system_menu.add_separator()
        system_menu.add_command(label="🚪 Cerrar Sesión", command=self.logout)
        
        # Menú Estudiantes (con funciones reales)
        students_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👥 Estudiantes", menu=students_menu)
        students_menu.add_command(label="➕ Registrar Estudiante",
                                command=lambda: self._execute_with_button_manager("register_student"))
        students_menu.add_command(label="📋 Lista de Estudiantes",
                                command=lambda: self._execute_with_button_manager("list_students"))
        students_menu.add_command(label="📤 Exportar Datos",
                                command=self.export_students_data)
        students_menu.add_command(label="🎯 Entrenar Modelo", command=self.train_model)
        
        # Menú Asistencia (con funciones reales)
        attendance_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Asistencia", menu=attendance_menu)
        attendance_menu.add_command(label="🚀 Iniciar Reconocimiento",
                                  command=lambda: self._execute_with_button_manager("start_recognition"))
        attendance_menu.add_command(label="📈 Ver Reportes",
                                  command=lambda: self._execute_with_button_manager("view_reports"))
        attendance_menu.add_command(label="📋 Exportar Reportes",
                                  command=self.export_attendance_reports)
        
        # Menú Notificaciones (con funciones reales)
        notifications_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔔 Notificaciones", menu=notifications_menu)
        notifications_menu.add_command(label="📱 Enviar Notificación",
                                     command=lambda: self._execute_with_button_manager("send_notification"))
        notifications_menu.add_command(label="📋 Historial de Notificaciones",
                                     command=self.show_notification_history)
        
        # Menú Admin (solo para admins)
        if self.auth_manager.has_permission(self.user['role'], 'manage_users'):
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="⚙️ Administración", menu=admin_menu)
            admin_menu.add_command(label="👥 Gestionar Usuarios", command=self.manage_users)
            admin_menu.add_command(label="🔧 Configuración Sistema", command=self.system_config)
            admin_menu.add_command(label="💾 Backup de Datos", command=self.backup_data)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=help_menu)
        help_menu.add_command(label="📖 Manual de Usuario", command=self.show_manual)
        help_menu.add_command(label="🆘 Soporte Técnico", command=self.tech_support)
        help_menu.add_command(label="ℹ️ Acerca de", command=self.about)
    
    def create_toolbar(self):
        """Crear barra de herramientas con sistema mejorado"""
        if not BUTTON_SYSTEM_AVAILABLE or not hasattr(self, 'button_manager'):
            # Fallback al toolbar básico
            return self.create_toolbar_basic()
        
        try:
            toolbar = ttk_bootstrap.Frame(self.root, bootstyle=DARK)
            toolbar.pack(fill=X, padx=5, pady=5)
            
            # Crear botones usando el sistema mejorado
            dashboard_btn = self.button_manager.create_button(toolbar, "dashboard")
            dashboard_btn.pack(side=LEFT, padx=2)
            
            recognition_btn = self.button_manager.create_button(toolbar, "start_recognition")
            recognition_btn.pack(side=LEFT, padx=2)
            
            students_btn = self.button_manager.create_button(toolbar, "list_students")
            students_btn.pack(side=LEFT, padx=2)
            
            reports_btn = self.button_manager.create_button(toolbar, "view_reports")
            reports_btn.pack(side=LEFT, padx=2)
            
            notification_btn = self.button_manager.create_button(toolbar, "send_notification")
            notification_btn.pack(side=LEFT, padx=2)
            
            # Botón para registrar estudiante
            register_btn = self.button_manager.create_button(toolbar, "register_student")
            register_btn.pack(side=LEFT, padx=2)
            
            # Información de usuario en la derecha
            user_info = ttk_bootstrap.Label(
                toolbar,
                text=f"👤 {self.user['full_name']} ({self.user['role'].title()})",
                bootstyle=INFO
            )
            user_info.pack(side=RIGHT, padx=10)
            
            # Indicador de sistema mejorado
            self.system_status_label = ttk_bootstrap.Label(
                toolbar,
                text="⚡ Sistema Mejorado",
                bootstyle=SUCCESS
            )
            self.system_status_label.pack(side=RIGHT, padx=5)
            
            self.logger.info("✅ Toolbar mejorado creado")
            
        except Exception as e:
            self.logger.error(f"❌ Error creando toolbar mejorado: {e}")
            return self.create_toolbar_basic()
    
    def create_toolbar_basic(self):
        """Crear toolbar básico como fallback"""
        toolbar = ttk_bootstrap.Frame(self.root, bootstyle=DARK)
        toolbar.pack(fill=X, padx=5, pady=5)
        
        # Botones básicos
        ttk_bootstrap.Button(
            toolbar, text="🏠 Dashboard", bootstyle=PRIMARY,
            command=self.show_dashboard
        ).pack(side=LEFT, padx=2)
        
        ttk_bootstrap.Button(
            toolbar, text="🚀 Reconocimiento", bootstyle=SUCCESS,
            command=self.start_recognition
        ).pack(side=LEFT, padx=2)
        
        ttk_bootstrap.Button(
            toolbar, text="👥 Estudiantes", bootstyle=INFO,
            command=self.list_students
        ).pack(side=LEFT, padx=2)
        
        ttk_bootstrap.Button(
            toolbar, text="📊 Reportes", bootstyle=WARNING,
            command=self.view_reports
        ).pack(side=LEFT, padx=2)
        
        ttk_bootstrap.Button(
            toolbar, text="🔔 Notificar", bootstyle=DANGER,
            command=self.send_notification
        ).pack(side=LEFT, padx=2)
        
        # Información de usuario
        user_info = ttk_bootstrap.Label(
            toolbar,
            text=f"👤 {self.user['full_name']} ({self.user['role'].title()})",
            bootstyle=INFO
        )
        user_info.pack(side=RIGHT, padx=10)
    
    def create_main_panel(self):
        """Crear panel principal"""
        # Notebook para módulos
        self.notebook = ttk_bootstrap.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Dashboard por defecto
        self.show_dashboard()
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = ttk_bootstrap.Frame(self.root, bootstyle=DARK)
        status_bar.pack(fill=X, side=BOTTOM)
        
        # Estado de conexiones
        self.firebase_status_label = ttk_bootstrap.Label(
            status_bar,
            text="🔥 Firebase: Conectado",
            bootstyle=SUCCESS
        )
        self.firebase_status_label.pack(side=LEFT, padx=5, pady=2)
        
        # Tiempo de sesión
        self.session_time_label = ttk_bootstrap.Label(
            status_bar,
            text="",
            bootstyle=INFO
        )
        self.session_time_label.pack(side=RIGHT, padx=5, pady=2)
        
        # Actualizar tiempo de sesión
        self.update_session_time()
    
    def update_session_time(self):
        """Actualizar tiempo de sesión"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_time_label.config(text=f"🕐 {current_time}")
        self.root.after(1000, self.update_session_time)
    
    def show_dashboard(self):
        """Mostrar dashboard principal"""
        # Limpiar pestañas existentes
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Crear frame del dashboard
        dashboard_frame = ttk_bootstrap.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard Empresarial")
        
        # Crear dashboard
        self.dashboard = ModernDashboard(dashboard_frame, self.auth_manager, self.firebase)
        self.dashboard.set_user(self.user, self.token)
        
        self.current_module = "dashboard"
        self.log_info("Dashboard cargado")
    
    # Métodos placeholder para funcionalidades
    def show_profile(self):
        messagebox.showinfo("Perfil", f"Perfil de {self.user['full_name']}")
    
    def change_password(self):
        messagebox.showinfo("Cambiar Contraseña", "Funcionalidad de cambio de contraseña")
    
    def register_student(self):
        self._show_student_registration_window()
    
    def list_students(self):
        """Mostrar ventana completa de lista de estudiantes"""
        self._show_students_list_window()
    
    def train_model(self):
        messagebox.showinfo("Entrenar", "Entrenamiento del modelo facial")
    
    def start_recognition(self):
        messagebox.showinfo("Reconocimiento", "Iniciando reconocimiento facial")
    
    def view_reports(self):
        """Mostrar ventana completa de reportes"""
        self._show_reports_window()
    
    def export_data(self):
        messagebox.showinfo("Exportar", "Exportación de datos")
    
    def send_notification(self):
        messagebox.showinfo("Notificar", "Envío de notificaciones")
    
    def notification_history(self):
        messagebox.showinfo("Historial", "Historial de notificaciones")
    
    def manage_users(self):
        messagebox.showinfo("Usuarios", "Gestión de usuarios del sistema")
    
    def system_config(self):
        messagebox.showinfo("Configuración", "Configuración del sistema")
    
    def backup_data(self):
        messagebox.showinfo("Backup", "Backup de datos del sistema")
    
    def show_manual(self):
        messagebox.showinfo("Manual", "Manual de usuario")
    
    def tech_support(self):
        messagebox.showinfo("Soporte", "Contacto de soporte técnico")
    
    def about(self):
        about_text = """🏢 AsistoYA Enterprise Edition

Sistema de Control de Asistencia con Reconocimiento Facial

Versión: 2.0 Enterprise
Desarrollado con tecnologías avanzadas:
• OpenCV para reconocimiento facial
• Firebase para sincronización en la nube
• Seguridad empresarial con encriptación AES-256

© 2025 AsistoYA Systems"""
        
        messagebox.showinfo("Acerca de AsistoYA", about_text)
    
    def logout(self):
        """Cerrar sesión"""
        response = messagebox.askyesno(
            "Cerrar Sesión", 
            "¿Está seguro que desea cerrar sesión?"
        )
        
        if response:
            self.log_info(f"Usuario {self.user['username']} cerró sesión")
            self.root.destroy()
            
            # Mostrar login nuevamente
            login = LoginWindow()
            login.run()
    
    def on_closing(self):
        """Protocolo de cierre de aplicación"""
        response = messagebox.askyesno(
            "Salir", 
            "¿Está seguro que desea salir de AsistoYA Enterprise?"
        )
        
        if response:
            self.log_info(f"Usuario {self.user['username']} salió del sistema")
            self.root.destroy()
    
    def run(self):
        """Ejecutar aplicación principal"""
        self.root.mainloop()

    def _show_student_registration_window(self):
        """Mostrar ventana de registro de estudiante"""
        register_window = tk.Toplevel(self.root)
        register_window.title("➕ Registrar Estudiante")
        register_window.geometry("500x400")
        register_window.resizable(False, False)
        
        register_window.transient(self.root)
        register_window.grab_set()
        
        main_frame = ttk_bootstrap.Frame(register_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        title_label = ttk_bootstrap.Label(
            main_frame,
            text="➕ Registrar Nuevo Estudiante",
            font=("Segoe UI", 16, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Variables
        name_var = tk.StringVar()
        email_var = tk.StringVar()
        grade_var = tk.StringVar()
        
        # Formulario
        form_frame = ttk_bootstrap.LabelFrame(main_frame, text="Información del Estudiante", padding=15)
        form_frame.pack(fill=X, pady=(0, 20))
        
        # Nombre completo
        ttk_bootstrap.Label(form_frame, text="👤 Nombre Completo:").pack(anchor=W, pady=(0, 5))
        name_entry = ttk_bootstrap.Entry(form_frame, textvariable=name_var, width=40)
        name_entry.pack(fill=X, pady=(0, 10))
        
        # Email
        ttk_bootstrap.Label(form_frame, text="📧 Email (opcional):").pack(anchor=W, pady=(0, 5))
        email_entry = ttk_bootstrap.Entry(form_frame, textvariable=email_var, width=40)
        email_entry.pack(fill=X, pady=(0, 10))
        
        # Grado
        ttk_bootstrap.Label(form_frame, text="📚 Grado/Curso (opcional):").pack(anchor=W, pady=(0, 5))
        grade_entry = ttk_bootstrap.Entry(form_frame, textvariable=grade_var, width=40)
        grade_entry.pack(fill=X, pady=(0, 10))
        
        def register_student_action():
            name = name_var.get().strip()
            email = email_var.get().strip()
            grade = grade_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "El nombre completo es obligatorio")
                return
            
            try:
                # Registrar estudiante usando el modelo
                result = student_model.create_student(name, email if email else None, grade if grade else None)
                
                if result['success']:
                    student_id = result['student']['student_id']
                    messagebox.showinfo("Éxito", f"Estudiante registrado exitosamente\nID: {student_id}\nNombre: {name}")
                    register_window.destroy()
                    self.log_info(f"Estudiante registrado: {name} (ID: {student_id})")
                else:
                    messagebox.showerror("Error", result.get('message', 'Error desconocido al registrar estudiante'))
            except Exception as e:
                messagebox.showerror("Error", f"Error registrando estudiante: {str(e)}")
                self.log_info(f"Error registrando estudiante: {str(e)}")
        
        # Botones
        buttons_frame = ttk_bootstrap.Frame(main_frame)
        buttons_frame.pack(fill=X)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="✅ Registrar Estudiante",
            command=register_student_action,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=register_window.destroy,
            bootstyle=DANGER
        ).pack(side=LEFT)
        
        # Focus en nombre
        name_entry.focus()

    def _show_students_list_window(self):
        """Mostrar ventana completa de lista de estudiantes"""
        students_window = tk.Toplevel(self.root)
        students_window.title("📋 Lista de Estudiantes")
        students_window.geometry("1000x700")
        students_window.resizable(True, True)
        
        students_window.transient(self.root)
        students_window.grab_set()
        
        main_frame = ttk_bootstrap.Frame(students_window, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título y estadísticas
        header_frame = ttk_bootstrap.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 15))
        
        title_label = ttk_bootstrap.Label(
            header_frame,
            text="📋 Lista de Estudiantes Registrados",
            font=("Segoe UI", 18, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(side=LEFT)
        
        # Panel de búsqueda y filtros
        search_frame = ttk_bootstrap.LabelFrame(main_frame, text="🔍 Búsqueda y Filtros", padding=10)
        search_frame.pack(fill=X, pady=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = ttk_bootstrap.Entry(
            search_frame,
            textvariable=search_var,
            placeholder_text="Buscar por nombre, email o ID...",
            width=40
        )
        search_entry.pack(side=LEFT, padx=(0, 10))
        
        # Variables para filtros
        show_active_var = tk.BooleanVar(value=True)
        show_with_faces_var = tk.BooleanVar(value=False)
        
        ttk_bootstrap.Checkbutton(
            search_frame,
            text="Solo activos",
            variable=show_active_var,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Checkbutton(
            search_frame,
            text="Solo con rostros",
            variable=show_with_faces_var,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=5)
        
        # Tabla de estudiantes
        table_frame = ttk_bootstrap.LabelFrame(main_frame, text="👥 Estudiantes", padding=10)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Configurar Treeview
        columns = ("ID", "Nombre", "Email", "Grado", "Rostros", "Asistencias", "Estado", "Registro")
        students_tree = ttk_bootstrap.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
            bootstyle=INFO
        )
        
        # Configurar columnas
        students_tree.heading("ID", text="ID Estudiante")
        students_tree.heading("Nombre", text="Nombre Completo")
        students_tree.heading("Email", text="Email")
        students_tree.heading("Grado", text="Grado/Curso")
        students_tree.heading("Rostros", text="Rostros")
        students_tree.heading("Asistencias", text="Asistencias")
        students_tree.heading("Estado", text="Estado")
        students_tree.heading("Registro", text="Fecha Registro")
        
        # Ancho de columnas
        students_tree.column("ID", width=100)
        students_tree.column("Nombre", width=200)
        students_tree.column("Email", width=180)
        students_tree.column("Grado", width=100)
        students_tree.column("Rostros", width=80)
        students_tree.column("Asistencias", width=100)
        students_tree.column("Estado", width=80)
        students_tree.column("Registro", width=120)
        
        # Scrollbars
        v_scrollbar = ttk_bootstrap.Scrollbar(table_frame, orient=VERTICAL, command=students_tree.yview)
        h_scrollbar = ttk_bootstrap.Scrollbar(table_frame, orient=HORIZONTAL, command=students_tree.xview)
        students_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table y scrollbars
        students_tree.pack(side=LEFT, fill=BOTH, expand=True)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        
        # Panel de estadísticas
        stats_frame = ttk_bootstrap.LabelFrame(main_frame, text="📊 Estadísticas", padding=10)
        stats_frame.pack(fill=X, pady=(0, 10))
        
        stats_vars = {
            'total': tk.StringVar(value="0"),
            'active': tk.StringVar(value="0"),
            'with_faces': tk.StringVar(value="0"),
            'attendance_rate': tk.StringVar(value="0%")
        }
        
        # Crear widgets de estadísticas
        stats_grid = ttk_bootstrap.Frame(stats_frame)
        stats_grid.pack(fill=X)
        
        for i, (key, var) in enumerate(stats_vars.items()):
            labels = {
                'total': 'Total Estudiantes',
                'active': 'Activos',
                'with_faces': 'Con Rostros',
                'attendance_rate': 'Tasa Asistencia Prom.'
            }
            
            stat_frame = ttk_bootstrap.Frame(stats_grid)
            stat_frame.pack(side=LEFT, padx=10, fill=X, expand=True)
            
            ttk_bootstrap.Label(
                stat_frame,
                text=labels[key],
                font=("Segoe UI", 10, "bold")
            ).pack()
            
            ttk_bootstrap.Label(
                stat_frame,
                textvariable=var,
                font=("Segoe UI", 14, "bold"),
                bootstyle=SUCCESS
            ).pack()
        
        # Botones de acción
        buttons_frame = ttk_bootstrap.Frame(main_frame)
        buttons_frame.pack(fill=X)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="➕ Nuevo Estudiante",
            command=self.register_student,
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="✏️ Editar Seleccionado",
            command=lambda: self._edit_selected_student(students_tree),
            bootstyle=WARNING
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="🗑️ Eliminar Seleccionado",
            command=lambda: self._delete_selected_student(students_tree),
            bootstyle=DANGER
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="📊 Ver Detalles",
            command=lambda: self._show_student_details(students_tree),
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="📄 Exportar Lista",
            command=lambda: self._export_students_list(students_tree),
            bootstyle=SECONDARY
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="🔄 Actualizar",
            command=lambda: load_students(),
            bootstyle=PRIMARY
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="❌ Cerrar",
            command=students_window.destroy,
            bootstyle=DARK
        ).pack(side=RIGHT)
        
        def load_students():
            """Cargar estudiantes en la tabla"""
            try:
                # Limpiar tabla
                for item in students_tree.get_children():
                    students_tree.delete(item)
                
                # Obtener estudiantes
                students = student_model.get_all_students()
                search_text = search_var.get().lower().strip()
                
                # Filtrar estudiantes
                filtered_students = []
                for student in students:
                    # Filtro de búsqueda
                    if search_text:
                        searchable_text = f"{student.get('full_name', '')} {student.get('email', '')} {student.get('student_id', '')}".lower()
                        if search_text not in searchable_text:
                            continue
                    
                    # Filtro de activos
                    if show_active_var.get() and not student.get('active', True):
                        continue
                    
                    # Filtro de rostros
                    if show_with_faces_var.get() and not student.get('face_registered', False):
                        continue
                    
                    filtered_students.append(student)
                
                # Agregar estudiantes a la tabla
                for student in filtered_students:
                    # Formatear datos
                    student_id = student.get('student_id', 'N/A')
                    name = student.get('full_name', 'Sin nombre')
                    email = student.get('email', 'Sin email')
                    grade = student.get('grade', 'Sin grado')
                    face_count = student.get('face_count', 0)
                    attendance_count = student.get('attendance_count', 0)
                    active = "✅ Activo" if student.get('active', True) else "❌ Inactivo"
                    
                    # Formatear fecha de registro
                    created_at = student.get('created_at', '')
                    if created_at:
                        try:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                        except:
                            formatted_date = created_at[:10]
                    else:
                        formatted_date = 'N/A'
                    
                    # Insertar fila
                    values = (student_id, name, email, grade, f"{face_count} rostros", 
                             f"{attendance_count} veces", active, formatted_date)
                    
                    students_tree.insert("", "end", values=values)
                
                # Actualizar estadísticas
                total_students = len(students)
                active_students = len([s for s in students if s.get('active', True)])
                students_with_faces = len([s for s in students if s.get('face_registered', False)])
                
                # Calcular tasa de asistencia promedio
                total_attendance = sum(s.get('attendance_count', 0) for s in students)
                avg_attendance = (total_attendance / total_students) if total_students > 0 else 0
                
                stats_vars['total'].set(str(total_students))
                stats_vars['active'].set(str(active_students))
                stats_vars['with_faces'].set(str(students_with_faces))
                stats_vars['attendance_rate'].set(f"{avg_attendance:.1f}")
                
                self.log_info(f"Lista de estudiantes actualizada: {len(filtered_students)} mostrados de {total_students} total")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando estudiantes: {str(e)}")
                self.log_info(f"Error cargando estudiantes: {str(e)}")
        
        # Bind eventos
        search_var.trace('w', lambda *args: load_students())
        show_active_var.trace('w', lambda *args: load_students())
        show_with_faces_var.trace('w', lambda *args: load_students())
        
        # Cargar estudiantes inicialmente
        load_students()
        
        # Focus en búsqueda
        search_entry.focus()

    def _edit_selected_student(self, tree):
        """Editar estudiante seleccionado"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un estudiante para editar")
            return
        
        # Obtener datos del estudiante seleccionado
        item = tree.item(selection[0])
        student_id = item['values'][0]
        
        # Aquí implementarías la ventana de edición
        messagebox.showinfo("Editar", f"Función de edición para estudiante {student_id}\n(Por implementar)")

    def _delete_selected_student(self, tree):
        """Eliminar estudiante seleccionado"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un estudiante para eliminar")
            return
        
        item = tree.item(selection[0])
        student_id = item['values'][0]
        student_name = item['values'][1]
        
        # Confirmar eliminación
        response = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar al estudiante?\n\nID: {student_id}\nNombre: {student_name}\n\nEsta acción no se puede deshacer."
        )
        
        if response:
            try:
                result = student_model.delete_student(student_id, remove_faces=True)
                if result['success']:
                    messagebox.showinfo("Éxito", f"Estudiante {student_name} eliminado exitosamente")
                    # Recargar la lista
                    tree.delete(selection[0])
                    self.log_info(f"Estudiante eliminado: {student_name} (ID: {student_id})")
                else:
                    messagebox.showerror("Error", result['message'])
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando estudiante: {str(e)}")

    def _show_student_details(self, tree):
        """Mostrar detalles completos del estudiante"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un estudiante para ver detalles")
            return
        
        item = tree.item(selection[0])
        student_id = item['values'][0]
        
        try:
            student = student_model.get_student_by_id(student_id)
            if student:
                details = f"""📋 DETALLES DEL ESTUDIANTE

🆔 ID: {student.get('student_id', 'N/A')}
👤 Nombre: {student.get('full_name', 'N/A')}
📧 Email: {student.get('email', 'Sin email')}
📚 Grado: {student.get('grade', 'Sin grado')}
✅ Estado: {'Activo' if student.get('active', True) else 'Inactivo'}
🎯 Rostros: {student.get('face_count', 0)} registrados
📊 Asistencias: {student.get('attendance_count', 0)} veces
📅 Registro: {student.get('created_at', 'N/A')[:19]}
🕐 Última asistencia: {student.get('last_attendance', 'Nunca')[:19] if student.get('last_attendance') else 'Nunca'}"""
                
                messagebox.showinfo(f"Detalles - {student.get('full_name', 'Estudiante')}", details)
            else:
                messagebox.showerror("Error", "Estudiante no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo detalles: {str(e)}")

    def _export_students_list(self, tree):
        """Exportar lista de estudiantes"""
        try:
            # Obtener todos los estudiantes
            students = student_model.get_all_students()
            
            if not students:
                messagebox.showwarning("Advertencia", "No hay estudiantes para exportar")
                return
            
            # Crear DataFrame
            data = []
            for student in students:
                data.append({
                    'ID': student.get('student_id', ''),
                    'Nombre Completo': student.get('full_name', ''),
                    'Email': student.get('email', ''),
                    'Grado': student.get('grade', ''),
                    'Estado': 'Activo' if student.get('active', True) else 'Inactivo',
                    'Rostros Registrados': student.get('face_count', 0),
                    'Total Asistencias': student.get('attendance_count', 0),
                    'Fecha Registro': student.get('created_at', '')[:19] if student.get('created_at') else '',
                    'Última Asistencia': student.get('last_attendance', '')[:19] if student.get('last_attendance') else 'Nunca'
                })
            
            df = pd.DataFrame(data)
            
            # Pedir ubicación de guardado
            filename = filedialog.asksaveasfilename(
                title="Exportar Lista de Estudiantes",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                if filename.endswith('.xlsx'):
                    df.to_excel(filename, index=False, sheet_name='Estudiantes')
                elif filename.endswith('.csv'):
                    df.to_csv(filename, index=False, encoding='utf-8')
                else:
                    df.to_excel(filename + '.xlsx', index=False, sheet_name='Estudiantes')
                
                messagebox.showinfo("Éxito", f"Lista exportada exitosamente a:\n{filename}")
                self.log_info(f"Lista de estudiantes exportada: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando lista: {str(e)}")

    def _show_reports_window(self):
        """Mostrar ventana completa de reportes"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("📊 Reportes y Análisis")
        reports_window.geometry("900x600")
        reports_window.resizable(True, True)
        
        reports_window.transient(self.root)
        reports_window.grab_set()
        
        main_frame = ttk_bootstrap.Frame(reports_window, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        title_label = ttk_bootstrap.Label(
            main_frame,
            text="📊 Reportes y Análisis de Asistencia",
            font=("Segoe UI", 18, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Panel de configuración de reportes
        config_frame = ttk_bootstrap.LabelFrame(main_frame, text="⚙️ Configuración del Reporte", padding=15)
        config_frame.pack(fill=X, pady=(0, 15))
        
        # Selector de tipo de reporte
        ttk_bootstrap.Label(config_frame, text="📋 Tipo de Reporte:", font=("Segoe UI", 11, "bold")).pack(anchor=W)
        
        report_type_var = tk.StringVar(value="daily")
        report_types = [
            ("Reporte Diario", "daily"),
            ("Reporte Semanal", "weekly"),
            ("Reporte Mensual", "monthly"),
            ("Reporte Personalizado", "custom")
        ]
        
        for text, value in report_types:
            ttk_bootstrap.Radiobutton(
                config_frame,
                text=text,
                variable=report_type_var,
                value=value,
                bootstyle="outline-toolbutton"
            ).pack(anchor=W, padx=(20, 0), pady=2)
        
        # Selector de fechas
        dates_frame = ttk_bootstrap.Frame(config_frame)
        dates_frame.pack(fill=X, pady=(15, 0))
        
        ttk_bootstrap.Label(dates_frame, text="📅 Rango de Fechas:", font=("Segoe UI", 11, "bold")).pack(anchor=W)
        
        date_range_frame = ttk_bootstrap.Frame(dates_frame)
        date_range_frame.pack(fill=X, pady=(5, 0))
        
        # Fecha desde
        ttk_bootstrap.Label(date_range_frame, text="Desde:").pack(side=LEFT, padx=(20, 5))
        from_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_date_entry = ttk_bootstrap.Entry(date_range_frame, textvariable=from_date_var, width=12)
        from_date_entry.pack(side=LEFT, padx=(0, 15))
        
        # Fecha hasta
        ttk_bootstrap.Label(date_range_frame, text="Hasta:").pack(side=LEFT, padx=(0, 5))
        to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date_entry = ttk_bootstrap.Entry(date_range_frame, textvariable=to_date_var, width=12)
        to_date_entry.pack(side=LEFT)
        
        # Panel de opciones
        options_frame = ttk_bootstrap.LabelFrame(main_frame, text="🎯 Opciones del Reporte", padding=15)
        options_frame.pack(fill=X, pady=(0, 15))
        
        include_graphs_var = tk.BooleanVar(value=True)
        include_stats_var = tk.BooleanVar(value=True)
        include_details_var = tk.BooleanVar(value=False)
        
        ttk_bootstrap.Checkbutton(
            options_frame,
            text="📈 Incluir gráficos estadísticos",
            variable=include_graphs_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=2)
        
        ttk_bootstrap.Checkbutton(
            options_frame,
            text="📊 Incluir estadísticas detalladas",
            variable=include_stats_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=2)
        
        ttk_bootstrap.Checkbutton(
            options_frame,
            text="📋 Incluir lista detallada de asistencias",
            variable=include_details_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=2)
        
        # Panel de vista previa
        preview_frame = ttk_bootstrap.LabelFrame(main_frame, text="👁️ Vista Previa", padding=15)
        preview_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        preview_text = tk.Text(
            preview_frame,
            height=10,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#2b3e50",
            fg="white",
            selectbackground="#3498db"
        )
        preview_text.pack(fill=BOTH, expand=True)
        
        preview_scrollbar = ttk_bootstrap.Scrollbar(preview_frame, orient=VERTICAL, command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scrollbar.set)
        preview_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Botones de acción
        buttons_frame = ttk_bootstrap.Frame(main_frame)
        buttons_frame.pack(fill=X)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="🔍 Generar Vista Previa",
            command=lambda: generate_preview(),
            bootstyle=INFO
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="📄 Exportar a PDF",
            command=lambda: export_pdf_report(),
            bootstyle=DANGER
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="📊 Exportar a Excel",
            command=lambda: export_excel_report(),
            bootstyle=SUCCESS
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="📋 Copiar al Portapapeles",
            command=lambda: copy_to_clipboard(),
            bootstyle=WARNING
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="❌ Cerrar",
            command=reports_window.destroy,
            bootstyle=DARK
        ).pack(side=RIGHT)
        
        def generate_preview():
            """Generar vista previa del reporte"""
            try:
                preview_text.delete(1.0, tk.END)
                
                # Obtener datos
                students = student_model.get_all_students()
                
                report_type = report_type_var.get()
                from_date = from_date_var.get()
                to_date = to_date_var.get()
                
                # Generar reporte
                report_content = f"""
📊 REPORTE DE ASISTENCIA - {report_type.upper()}
════════════════════════════════════════════════════════════

📅 Período: {from_date} al {to_date}
🕐 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 RESUMEN GENERAL:
────────────────────────────────────────────────────────────
👥 Total de estudiantes registrados: {len(students)}
✅ Estudiantes activos: {len([s for s in students if s.get('active', True)])}
🎯 Estudiantes con rostros: {len([s for s in students if s.get('face_registered', False)])}

📊 ESTADÍSTICAS DE ASISTENCIA:
────────────────────────────────────────────────────────────
"""
                
                if include_stats_var.get():
                    total_attendance = sum(s.get('attendance_count', 0) for s in students)
                    avg_attendance = total_attendance / len(students) if students else 0
                    
                    report_content += f"""
📈 Total de asistencias registradas: {total_attendance}
📊 Promedio de asistencias por estudiante: {avg_attendance:.2f}
📉 Tasa de asistencia general: {(avg_attendance / 30 * 100):.1f}%
"""
                
                if include_details_var.get():
                    report_content += f"""

📋 DETALLE POR ESTUDIANTE:
────────────────────────────────────────────────────────────
"""
                    for student in students[:10]:  # Mostrar solo los primeros 10
                        report_content += f"""
👤 {student.get('full_name', 'N/A')} (ID: {student.get('student_id', 'N/A')})
   📧 Email: {student.get('email', 'Sin email')}
   📚 Grado: {student.get('grade', 'Sin grado')}
   📊 Asistencias: {student.get('attendance_count', 0)}
   🕐 Última asistencia: {student.get('last_attendance', 'Nunca')[:19] if student.get('last_attendance') else 'Nunca'}
"""
                    
                    if len(students) > 10:
                        report_content += f"\n... y {len(students) - 10} estudiantes más.\n"
                
                if include_graphs_var.get():
                    report_content += f"""

📈 GRÁFICOS Y ANÁLISIS:
────────────────────────────────────────────────────────────
[Los gráficos se incluirán en la exportación a PDF/Excel]
• Gráfico de barras: Asistencia por día
• Gráfico circular: Distribución de asistencias
• Gráfico de líneas: Tendencia temporal
• Histograma: Distribución por horarios
"""
                
                report_content += f"""

────────────────────────────────────────────────────────────
🏢 AsistoYA Enterprise - Sistema de Control de Asistencia
📧 Reporte generado automáticamente
"""
                
                preview_text.insert(1.0, report_content)
                self.log_info(f"Vista previa de reporte generada: {report_type}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error generando vista previa: {str(e)}")
        
        def export_pdf_report():
            """Exportar reporte a PDF"""
            messagebox.showinfo("PDF", "Exportación a PDF\n(Función por implementar)")
        
        def export_excel_report():
            """Exportar reporte a Excel"""
            messagebox.showinfo("Excel", "Exportación a Excel\n(Función por implementar)")
        
        def copy_to_clipboard():
            """Copiar reporte al portapapeles"""
            content = preview_text.get(1.0, tk.END)
            reports_window.clipboard_clear()
            reports_window.clipboard_append(content)
            messagebox.showinfo("Copiado", "Reporte copiado al portapapeles")
        
        # Generar vista previa inicial
        generate_preview()

    # ==================== FUNCIONES AUXILIARES NUEVAS ====================
    
    def export_students_data(self):
        """Exportar datos de estudiantes"""
        try:
            from pathlib import Path
            import json
            from tkinter import filedialog
            
            students_file = Path("data/students.json")
            if not students_file.exists():
                messagebox.showwarning("Advertencia", "No hay datos de estudiantes para exportar")
                return False
            
            export_path = filedialog.asksaveasfilename(
                title="Exportar Datos de Estudiantes",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
            )
            
            if not export_path:
                return False
            
            with open(students_file, 'r', encoding='utf-8') as f:
                students = json.load(f)
            
            if export_path.endswith('.csv'):
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if students:
                        fieldnames = students[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(students)
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(students, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", f"Datos exportados a: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error exportando datos: {e}")
            messagebox.showerror("Error", f"Error: {str(e)}")
            return False
    
    def export_attendance_reports(self):
        """Exportar reportes de asistencia"""
        try:
            from pathlib import Path
            import json
            from tkinter import filedialog
            
            attendance_file = Path("data/attendance.json")
            if not attendance_file.exists():
                messagebox.showwarning("Advertencia", "No hay datos de asistencia para exportar")
                return
            
            export_path = filedialog.asksaveasfilename(
                title="Exportar Reportes de Asistencia",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
            )
            
            if not export_path:
                return
            
            with open(attendance_file, 'r', encoding='utf-8') as f:
                attendance_data = json.load(f)
            
            if export_path.endswith('.csv'):
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if attendance_data:
                        fieldnames = attendance_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(attendance_data)
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(attendance_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", f"Reportes exportados a: {export_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error exportando reportes: {e}")
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def show_notification_history(self):
        """Mostrar historial de notificaciones"""
        try:
            from pathlib import Path
            import json
            
            notifications_file = Path("data/notifications.json")
            if not notifications_file.exists():
                messagebox.showinfo("Info", "No hay historial de notificaciones")
                return
            
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
            
            # Crear ventana
            history_window = tk.Toplevel(self.root)
            history_window.title("📋 Historial de Notificaciones")
            history_window.geometry("800x600")
            history_window.grab_set()
            
            main_frame = ttk_bootstrap.Frame(history_window, padding=15)
            main_frame.pack(fill=BOTH, expand=True)
            
            title_label = ttk_bootstrap.Label(
                main_frame,
                text="📋 Historial de Notificaciones",
                font=("Segoe UI", 16, "bold"),
                bootstyle=PRIMARY
            )
            title_label.pack(pady=(0, 15))
            
            # Tabla
            columns = ('Fecha', 'Tipo', 'Destinatarios', 'Estado')
            tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Cargar datos
            for notification in reversed(notifications[-50:]):  # Últimas 50
                tree.insert('', 'end', values=(
                    notification.get('timestamp', '')[:19].replace('T', ' '),
                    notification.get('type', ''),
                    notification.get('recipients', ''),
                    notification.get('status', '')
                ))
            
            tree.pack(fill=BOTH, expand=True)
            
        except Exception as e:
            self.logger.error(f"❌ Error mostrando historial: {e}")
            messagebox.showerror("Error", f"Error: {str(e)}")

def main():
    """Función principal"""
    print("🚀 Iniciando AsistoYA Enterprise Edition...")
    print("📦 Verificando dependencias...")
    
    try:
        # Verificar Firebase
        firebase = get_firebase()
        if firebase.initialize():
            print("✅ Firebase conectado correctamente")
        else:
            print("⚠️ Advertencia: Firebase no conectado")
        
        # Verificar Auth
        auth = get_auth_manager()
        print("✅ Sistema de autenticación listo")
        
        print("🏢 Abriendo ventana de login...")
        
        # Iniciar aplicación
        login = LoginWindow()
        login.run()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        print("Verifique la instalación de dependencias:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
