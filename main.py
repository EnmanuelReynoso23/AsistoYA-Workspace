import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sys
import json

# Verificar si hay configuración fallback
USE_FALLBACK = "--fallback" in sys.argv
CONFIG = {
    "USE_YOLO": False,
    "CAMERA_INDEX": 0,
    "FACE_CONFIDENCE_THRESHOLD": 80,
    "SEND_NOTIFICATIONS": False
}

# Cargar configuración si existe
if os.path.exists("config.json"):
    try:
        with open("config.json", "r") as f:
            CONFIG.update(json.load(f))
        print(f"[INFO] Configuración cargada: {CONFIG}")
    except Exception as e:
        print(f"[ERROR] Error al cargar la configuración: {e}")

from user_interface import UserInterface
from database import Database
from security import Security
from login import LoginScreen
from models import SchoolManager
from dashboard import Dashboard
from attendance import AttendanceManager
from notifications import NotificationManager
from face_recognition_manager import FaceRecognitionManager
from registration_manager import RegistrationWindow
import tkinter as tk
from tkinter import messagebox

class AsistoYaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asisto Ya - Sistema de Asistencia con Reconocimiento Facial")
        
        # Configure size and center window
        width, height = 1024, 768
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Initialize components
        self.setup_database()
        self.security = Security()
        self.school_manager = SchoolManager()
        self.attendance_manager = AttendanceManager(self.database)
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(
            api_url="https://api.whatsapp.com/send",
            api_key="YOUR_API_KEY"
        )
        
        # Initialize user interface and connect components
        self.user_interface = UserInterface(self.root, self.database, self.security)
        self.user_interface.school_manager = self.school_manager
        self.user_interface.attendance_manager = self.attendance_manager
        self.user_interface.notification_manager = self.notification_manager
        
        # Create dashboard
        self.dashboard = None
        
        # Create face recognition manager
        self.face_manager = FaceRecognitionManager()
        
        # Set up menu bar
        self.create_menu_bar()
        
        # Load login screen
        self.create_login_screen()
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        self.menubar = tk.Menu(self.root)
          # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Dashboard", command=self.show_dashboard)
        file_menu.add_command(label="Asistencia", command=self.show_attendance)
        file_menu.add_separator()
        file_menu.add_command(label="Cerrar sesión", command=self.logout)
        file_menu.add_command(label="Salir", command=self.exit_app)
        self.menubar.add_cascade(label="Archivo", menu=file_menu)
        
        # Reports menu
        report_menu = tk.Menu(self.menubar, tearoff=0)
        report_menu.add_command(label="Exportar a Excel", command=self.export_excel_report)
        report_menu.add_command(label="Exportar a PDF", command=self.export_pdf_report)
        self.menubar.add_cascade(label="Reportes", menu=report_menu)
        
        # Administration menu
        admin_menu = tk.Menu(self.menubar, tearoff=0)
        admin_menu.add_command(label="Gestionar Registros", command=self.show_registration_management)
        admin_menu.add_separator()
        admin_menu.add_command(label="Configuración de Sistema", command=self.show_settings)
        self.menubar.add_cascade(label="Administración", menu=admin_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Ayuda", command=self.show_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        self.menubar.add_cascade(label="Ayuda", menu=help_menu)
        
    def setup_database(self):
        """Configure database, using in-memory storage if Firebase integration isn't available"""
        try:
            if os.path.exists("firebase_service_account.json"):
                self.database = Database(
                    cred_path="firebase_service_account.json",
                    db_url="https://asistoya-demo-default-rtdb.firebaseio.com/"
                )
                print("Firebase database configured successfully")
            else:
                print("Credentials file not found, using in-memory storage")
                self.database = None
        except Exception as e:
            print(f"Error configuring database: {e}")
            self.database = None

    def create_login_screen(self):
        """Create and display the login screen"""
        self.login_screen = LoginScreen(
            self.root, 
            self.security, 
            self.handle_login_success,
            self.handle_tutor_login_success  # Añadir manejador para login de tutores
        )

    def handle_login_success(self, username):
        """Handle successful admin login"""
        print(f"Admin login success: {username}")
        self.current_user = username
        self.user_interface.load_main_interface()
        self.root.config(menu=self.menubar)
    
    def handle_tutor_login_success(self, tutor_data):
        """Handle successful tutor login with access code"""
        print(f"Tutor login success: {tutor_data}")
        
        try:
            # Mostrar la vista específica para tutores
            student_id = tutor_data.get('student_id')
            course_id = tutor_data.get('course_id')
            
            # Asegurarse de que existe el estudiante
            if student_id not in self.school_manager.students:
                messagebox.showerror(
                    "Error", 
                    "No se encontró información del estudiante asociado a este código de acceso."
                )
                return
            
            # Crear vista para tutores (importación local para evitar dependencias circulares)
            from tutor_view import TutorView
            self.tutor_view = TutorView(
                self.root,
                self.security,
                self.school_manager,
                tutor_data,
                self.attendance_manager
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la vista de tutor: {str(e)}")
            print(f"Error en inicio de sesión de tutor: {e}")

    def create_tutor_interface(self, student):
        """Create simplified interface for tutors"""
        # Hide the menu for tutors
        self.root.config(menu="")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        title = ttk.Label(header_frame, text=f"Portal de Tutor - {student.full_name()}", 
                        font=("Arial", 16, "bold"))
        title.pack(side=tk.LEFT)
        
        logout_btn = ttk.Button(header_frame, text="Cerrar Sesión", 
                             command=self.logout, bootstyle="danger")
        logout_btn.pack(side=tk.RIGHT)
        
        # Student info section
        info_frame = ttk.LabelFrame(main_frame, text="Información del Estudiante", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Nombre: {student.full_name()}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Código: {student.code}").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Email: {student.email}").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Attendance summary section
        summary_frame = ttk.LabelFrame(main_frame, text="Resumen de Asistencia", padding=10)
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Table for attendance records
        columns = ("Fecha", "Curso", "Estado")
        attendance_table = ttk.Treeview(summary_frame, columns=columns, show="headings")
        
        for col in columns:
            attendance_table.heading(col, text=col)
            attendance_table.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=attendance_table.yview)
        attendance_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        attendance_table.pack(fill=tk.BOTH, expand=True)
        
        # Get attendance data for this student
        attendance_records = [r for r in self.attendance_manager.attendance_records 
                           if r["Student ID"] == student.code]
        
        # Sort by date, most recent first
        attendance_records.sort(key=lambda x: x["Date"], reverse=True)
        
        # Add records to table
        for record in attendance_records:
            course_code = record.get("Course", "")
            course_name = self.school_manager.courses[course_code].name if course_code in self.school_manager.courses else course_code
            
            attendance_table.insert("", tk.END, values=(
                record["Date"],
                course_name,
                record["Status"]
            ))

    def show_dashboard(self):
        """Show the dashboard view"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create dashboard if it doesn't exist
        self.dashboard = Dashboard(self.root, self.school_manager, self.attendance_manager)
        self.dashboard.show()
        
    def show_attendance(self):
        """Show the attendance interface"""
        # Clear existing widgets and show main interface
        self.user_interface.load_main_interface()
        
    def show_registration_management(self):
        """Show the registration management window"""
        try:
            registration_window = RegistrationWindow(self.root, self.security, self.school_manager)
            registration_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la gestión de registros: {str(e)}")
            print(f"Error al mostrar gestión de registros: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Configuración", "Configuración avanzada de AsistoYA.\nFuncionalidad en desarrollo.")
        
    def export_excel_report(self):
        """Export attendance report to Excel"""
        try:
            file_path = self.attendance_manager.export_report_to_excel()
            if file_path:
                messagebox.showinfo("Exportar Reporte", f"Reporte exportado exitosamente a:\n{file_path}")
            else:
                messagebox.showerror("Error", "No se pudo exportar el reporte.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        
    def export_pdf_report(self):
        """Export attendance report to PDF"""
        try:
            file_path = self.attendance_manager.export_report_to_pdf()
            if file_path:
                messagebox.showinfo("Exportar Reporte", f"Reporte exportado exitosamente a:\n{file_path}")
            else:
                messagebox.showerror("Error", "No se pudo exportar el reporte.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
        
    def show_help(self):
        """Show help information"""
        messagebox.showinfo("Ayuda", 
                          "AsistoYA - Sistema de Asistencia con Reconocimiento Facial\n\n"
                          "1. Registre estudiantes con la opción 'Registrar estudiante'\n"
                          "2. Cree cursos con la opción 'Crear curso'\n"
                          "3. Seleccione un curso activo para registrar asistencia\n"
                          "4. Use la cámara para la detección automática o registre manualmente\n"
                          "5. Exporte reportes desde el menú Reportes")
        
    def show_about(self):
        """Show about information"""
        messagebox.showinfo("Acerca de", 
                          "AsistoYA v1.0\n"
                          "Sistema de Asistencia con Reconocimiento Facial\n\n"
                          "Desarrollado como parte del proyecto educativo.\n\n"
                          "© 2025 AsistoYA")
        
    def logout(self):
        """Log out and return to login screen"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar la sesión?"):
            # Hide menu
            self.root.config(menu="")
            # Show login screen
            self.create_login_screen()
        
    def exit_app(self):
        """Exit the application with confirmation"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir de la aplicación?"):
            self.root.quit()

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = AsistoYaApp(root)
    root.mainloop()
