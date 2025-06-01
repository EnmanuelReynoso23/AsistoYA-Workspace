"""
🔧 Button System Integration - Parche para AsistoYA
Integración del sistema de gestión de botones mejorado
"""

import sys
from pathlib import Path

# Agregar paths
sys.path.append(str(Path(__file__).parent))

def patch_asistoya_buttons():
    """Aplicar parche al sistema de botones de AsistoYA"""
    
    # Código para reemplazar en asistoya.py
    button_integration_code = '''
# ==================== INTEGRACIÓN SISTEMA DE BOTONES MEJORADO ====================

# Importar sistemas mejorados
try:
    from ui.button_manager import ButtonManager, ButtonConfig, ButtonState, get_button_manager
    from ui.functional_handlers import FunctionalHandlers, get_functional_handlers
    BUTTON_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Sistema de botones mejorado no disponible: {e}")
    BUTTON_SYSTEM_AVAILABLE = False

def setup_enhanced_button_system(self):
    """Configurar sistema de botones mejorado"""
    if not BUTTON_SYSTEM_AVAILABLE:
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
        style="primary",
        tooltip="Mostrar panel principal con estadísticas"
    )
    self.button_manager.register_button(dashboard_config)
    
    # Botón Registro de Estudiantes
    register_config = ButtonConfig(
        button_id="register_student",
        text="👥 Registrar Estudiante",
        command=self.functional_handlers.register_student_real,
        style="success",
        tooltip="Registrar nuevo estudiante con captura facial",
        permissions=["manage_students"],
        validation_func=lambda: self._validate_camera_access()
    )
    self.button_manager.register_button(register_config)
    
    # Botón Lista de Estudiantes
    list_students_config = ButtonConfig(
        button_id="list_students",
        text="📋 Lista Estudiantes",
        command=self.functional_handlers.list_students_real,
        style="info",
        tooltip="Ver y gestionar estudiantes registrados"
    )
    self.button_manager.register_button(list_students_config)
    
    # Botón Reconocimiento Facial
    recognition_config = ButtonConfig(
        button_id="start_recognition",
        text="🚀 Reconocimiento",
        command=self.functional_handlers.start_recognition_real,
        style="success",
        tooltip="Iniciar reconocimiento facial para asistencia",
        permissions=["manage_attendance"],
        validation_func=lambda: self._validate_camera_access()
    )
    self.button_manager.register_button(recognition_config)
    
    # Botón Ver Reportes
    reports_config = ButtonConfig(
        button_id="view_reports",
        text="📊 Reportes",
        command=self.functional_handlers.view_reports_real,
        style="warning",
        tooltip="Ver reportes y estadísticas de asistencia"
    )
    self.button_manager.register_button(reports_config)
    
    # Botón Enviar Notificaciones
    notification_config = ButtonConfig(
        button_id="send_notification",
        text="🔔 Notificar",
        command=self.functional_handlers.send_notification_real,
        style="danger",
        tooltip="Enviar notificaciones a padres de familia",
        permissions=["send_notifications"]
    )
    self.button_manager.register_button(notification_config)

def create_enhanced_toolbar(self):
    """Crear toolbar con sistema de botones mejorado"""
    if not BUTTON_SYSTEM_AVAILABLE:
        # Fallback al toolbar original
        return self.create_toolbar_original()
    
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
        
        # Indicador de estado del sistema
        self.system_status_label = ttk_bootstrap.Label(
            toolbar,
            text="✅ Sistema Mejorado",
            bootstyle=SUCCESS
        )
        self.system_status_label.pack(side=RIGHT, padx=5)
        
        self.logger.info("✅ Toolbar mejorado creado")
        return True
        
    except Exception as e:
        self.logger.error(f"❌ Error creando toolbar mejorado: {e}")
        return self.create_toolbar_original()

def create_enhanced_menu(self):
    """Crear menú con funciones mejoradas"""
    if not BUTTON_SYSTEM_AVAILABLE:
        return self.create_menu_bar_original()
    
    try:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Sistema
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🏢 Sistema", menu=system_menu)
        system_menu.add_command(label="🏠 Dashboard", command=self.show_dashboard_enhanced)
        system_menu.add_separator()
        system_menu.add_command(label="👤 Perfil de Usuario", command=self.show_profile)
        system_menu.add_command(label="🔄 Cambiar Contraseña", command=self.change_password)
        system_menu.add_separator()
        system_menu.add_command(label="📊 Estadísticas de Botones", command=self.show_button_stats)
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
                                command=self.functional_handlers.export_students_data)
        
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
        
        # Menú Admin
        if self.auth_manager.has_permission(self.user['role'], 'manage_users'):
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="⚙️ Administración", menu=admin_menu)
            admin_menu.add_command(label="👥 Gestionar Usuarios", command=self.manage_users)
            admin_menu.add_command(label="🔧 Configuración Sistema", command=self.system_config)
            admin_menu.add_command(label="💾 Backup de Datos", command=self.backup_data)
            admin_menu.add_separator()
            admin_menu.add_command(label="🐛 Modo Debug Botones", command=self.toggle_button_debug)
            admin_menu.add_command(label="🔄 Resetear Estadísticas", command=self.reset_button_stats)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=help_menu)
        help_menu.add_command(label="📖 Manual de Usuario", command=self.show_manual)
        help_menu.add_command(label="🆘 Soporte Técnico", command=self.tech_support)
        help_menu.add_command(label="ℹ️ Acerca de", command=self.about)
        
        self.logger.info("✅ Menú mejorado creado")
        return True
        
    except Exception as e:
        self.logger.error(f"❌ Error creando menú mejorado: {e}")
        return self.create_menu_bar_original()

def _execute_with_button_manager(self, button_id):
    """Ejecutar comando usando el button manager"""
    if BUTTON_SYSTEM_AVAILABLE and hasattr(self, 'button_manager'):
        if button_id in self.button_manager.buttons:
            self.button_manager.buttons[button_id].command()
        else:
            self.logger.warning(f"⚠️ Botón no registrado: {button_id}")

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

# Función para aplicar el parche
def apply_button_system_patch(app_instance):
    """Aplicar parche del sistema de botones a la instancia de la aplicación"""
    
    # Agregar métodos mejorados a la instancia
    app_instance.setup_enhanced_button_system = lambda: setup_enhanced_button_system(app_instance)
    app_instance._register_button_configs = lambda: _register_button_configs(app_instance)
    app_instance.create_enhanced_toolbar = lambda: create_enhanced_toolbar(app_instance)
    app_instance.create_enhanced_menu = lambda: create_enhanced_menu(app_instance)
    app_instance._execute_with_button_manager = lambda button_id: _execute_with_button_manager(app_instance, button_id)
    app_instance._validate_camera_access = lambda: _validate_camera_access()
    app_instance.show_dashboard_enhanced = lambda: show_dashboard_enhanced(app_instance)
    app_instance.show_button_stats = lambda: show_button_stats(app_instance)
    app_instance.reset_button_stats = lambda: reset_button_stats(app_instance)
    app_instance.toggle_button_debug = lambda: toggle_button_debug(app_instance)
    app_instance.show_notification_history = lambda: show_notification_history(app_instance)
    app_instance.export_attendance_reports = lambda: export_attendance_reports(app_instance)
    
    # Guardar métodos originales
    app_instance.create_toolbar_original = app_instance.create_toolbar
    app_instance.create_menu_bar_original = app_instance.create_menu_bar
    
    # Reemplazar métodos originales con versiones mejoradas
    app_instance.create_toolbar = app_instance.create_enhanced_toolbar
    app_instance.create_menu_bar = app_instance.create_enhanced_menu
    
    # Configurar sistema mejorado
    if app_instance.setup_enhanced_button_system():
        app_instance.logger.info("🚀 Sistema de botones mejorado aplicado exitosamente")
        return True
    else:
        app_instance.logger.warning("⚠️ Fallback a sistema de botones original")
        return False
'''
    
    return button_integration_code

if __name__ == "__main__":
    print("🔧 Button System Integration - Parche para AsistoYA")
    print("Este archivo contiene el código de integración para el sistema de botones mejorado")
    print("Debe ser importado y aplicado en la aplicación principal")