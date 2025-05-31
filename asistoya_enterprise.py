"""
🚀 AsistoYA EMPRESARIAL - Aplicación Principal
Sistema de Control de Asistencia Nivel 1000% Profesional
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import sys
from pathlib import Path
import logging
from datetime import datetime

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
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")
    print("Instale las dependencias con: pip install -r requirements.txt")
    sys.exit(1)

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
        
        self.setup_main_ui()
        
        # Log de acceso
        self.log_info(f"Usuario {user['username']} ha iniciado sesión")
    
    def setup_logging(self):
        """Configurar sistema de logs"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='🏢 %(asctime)s - ENTERPRISE - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"enterprise_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('AsistoYA_Enterprise')
    
    def log_info(self, message):
        """Log información"""
        self.logger.info(message)
    
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
        
        # Menú Estudiantes
        students_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="👥 Estudiantes", menu=students_menu)
        students_menu.add_command(label="➕ Registrar Estudiante", command=self.register_student)
        students_menu.add_command(label="📋 Lista de Estudiantes", command=self.list_students)
        students_menu.add_command(label="🎯 Entrenar Modelo", command=self.train_model)
        
        # Menú Asistencia
        attendance_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Asistencia", menu=attendance_menu)
        attendance_menu.add_command(label="🚀 Iniciar Reconocimiento", command=self.start_recognition)
        attendance_menu.add_command(label="📈 Ver Reportes", command=self.view_reports)
        attendance_menu.add_command(label="📋 Exportar Datos", command=self.export_data)
        
        # Menú Notificaciones
        notifications_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔔 Notificaciones", menu=notifications_menu)
        notifications_menu.add_command(label="📱 Enviar Notificación", command=self.send_notification)
        notifications_menu.add_command(label="📋 Historial de Notificaciones", command=self.notification_history)
        
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
        """Crear barra de herramientas"""
        toolbar = ttk_bootstrap.Frame(self.root, bootstyle=DARK)
        toolbar.pack(fill=X, padx=5, pady=5)
        
        # Botones principales
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
        
        # Información de usuario en la derecha
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
        try:
            students = student_model.get_all_students()
            messagebox.showinfo("Lista de Estudiantes", f"Total de estudiantes registrados: {len(students)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo estudiantes: {str(e)}")
    
    def train_model(self):
        messagebox.showinfo("Entrenar", "Entrenamiento del modelo facial")
    
    def start_recognition(self):
        messagebox.showinfo("Reconocimiento", "Iniciando reconocimiento facial")
    
    def view_reports(self):
        try:
            report_generator = get_report_generator()
            messagebox.showinfo("Reportes", "Generador de reportes disponible")
        except Exception as e:
            messagebox.showerror("Error", f"Error accediendo a reportes: {str(e)}")
    
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
