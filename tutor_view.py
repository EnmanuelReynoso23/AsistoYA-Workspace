import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TutorView:
    """Vista especial para tutores que acceden con código de acceso"""
    
    def __init__(self, root, security, school_manager, student_code, course_code):
        """Inicializa la vista para tutores
        
        Args:
            root: La raíz de la aplicación tkinter
            security: El objeto de seguridad para validar los códigos de acceso
            school_manager: El gestor de la escuela para acceder a datos
            student_code: El código del estudiante
            course_code: El código del curso
        """
        self.root = root
        self.security = security
        self.school_manager = school_manager
        self.student_code = student_code
        self.course_code = course_code
        
        # Verificar que el estudiante y curso existan
        if student_code not in self.school_manager.students:
            raise ValueError(f"No se encontró estudiante con código {student_code}")
            
        if course_code not in self.school_manager.courses:
            raise ValueError(f"No se encontró curso con código {course_code}")
            
        # Guardar referencias
        self.student = self.school_manager.students[student_code]
        self.course = self.school_manager.courses[course_code]
        
        # Limpiar la interfaz actual
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configuración de la ventana
        self.root.title(f"AsistoYA - Vista de Tutor - {self.student.full_name()}")
        
        # Crear widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Crea los widgets de la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text=f"Registro de Asistencia - {self.student.full_name()}",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            header_frame,
            text="Cerrar Sesión",
            bootstyle="secondary",
            command=self.logout
        ).pack(side=tk.RIGHT)
        
        # Información del estudiante
        student_frame = ttk.LabelFrame(main_frame, text="Información del Estudiante", padding=10)
        student_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(student_frame, text=f"Nombre: {self.student.full_name()}", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Label(student_frame, text=f"Código: {self.student_code}", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Label(student_frame, text=f"Email: {self.student.email}", font=("Arial", 12)).pack(anchor=tk.W)
        
        # Información del curso
        course_frame = ttk.LabelFrame(main_frame, text="Información del Curso", padding=10)
        course_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(course_frame, text=f"Curso: {self.course.name}", font=("Arial", 12)).pack(anchor=tk.W)
        ttk.Label(course_frame, text=f"Código: {self.course_code}", font=("Arial", 12)).pack(anchor=tk.W)
        
        if hasattr(self.course, "professor") and self.course.professor:
            prof_name = self.school_manager.professors[self.course.professor].full_name()
            ttk.Label(course_frame, text=f"Profesor: {prof_name}", font=("Arial", 12)).pack(anchor=tk.W)
        
        # Registro de asistencia (tabla)
        attendance_frame = ttk.LabelFrame(main_frame, text="Registro de Asistencia", padding=10)
        attendance_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Crear tabla de asistencia
        columns = ("Fecha", "Estado", "Hora")
        self.attendance_table = ttk.Treeview(attendance_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.attendance_table.heading(col, text=col)
            self.attendance_table.column(col, width=100)
            
        # Scrollbar
        scrollbar = ttk.Scrollbar(attendance_frame, orient=tk.VERTICAL, command=self.attendance_table.yview)
        self.attendance_table.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar elementos
        self.attendance_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos de asistencia
        self.load_attendance_data()
        
        # Gráfico de asistencia
        graph_frame = ttk.LabelFrame(main_frame, text="Estadísticas de Asistencia", padding=10)
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear gráfico
        self.create_attendance_chart(graph_frame)
        
    def load_attendance_data(self):
        """Carga los datos de asistencia en la tabla"""
        # Limpiar tabla
        for item in self.attendance_table.get_children():
            self.attendance_table.delete(item)
            
        # Obtener datos de asistencia
        attendance_data = []
        
        for date, records in self.course.attendance.items():
            if self.student_code in records:
                status = records[self.student_code]
                # Si tiene formato de timestamp, extraer la hora
                time_str = "N/A"
                if isinstance(status, dict) and "timestamp" in status:
                    time_obj = datetime.fromtimestamp(status["timestamp"])
                    time_str = time_obj.strftime("%H:%M")
                    status = status["status"]
                
                attendance_data.append((date, status, time_str))
        
        # Ordenar por fecha (más reciente primero)
        attendance_data.sort(key=lambda x: x[0], reverse=True)
        
        # Insertar en la tabla
        for date, status, time_str in attendance_data:
            # Convertir formato de fecha a más legible
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d/%m/%Y")
            except:
                formatted_date = date
                
            self.attendance_table.insert("", tk.END, values=(formatted_date, status, time_str))
            
    def create_attendance_chart(self, parent_frame):
        """Crea un gráfico con estadísticas de asistencia"""
        # Contar asistencias por tipo
        status_counts = {"Presente": 0, "Ausente": 0, "Tardanza": 0}
        
        for date, records in self.course.attendance.items():
            if self.student_code in records:
                status = records[self.student_code]
                if isinstance(status, dict) and "status" in status:
                    status = status["status"]
                    
                # Normalizar estados
                status_lower = status.lower()
                if "presente" in status_lower:
                    status_counts["Presente"] += 1
                elif "ausente" in status_lower:
                    status_counts["Ausente"] += 1
                elif "tard" in status_lower:  # "tardanza" o "tarde"
                    status_counts["Tardanza"] += 1
        
        # Crear figura de matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Gráfico de barras
        labels = list(status_counts.keys())
        values = list(status_counts.values())
        
        ax1.bar(labels, values, color=["green", "red", "orange"])
        ax1.set_title("Registro de Asistencia")
        ax1.set_ylabel("Cantidad")
        
        # Calcular porcentaje de asistencia
        total = sum(values)
        if total > 0:
            attendance_percentage = (status_counts["Presente"] / total) * 100
        else:
            attendance_percentage = 0
            
        # Gráfico circular
        colors = ["green", "red", "orange"]
        explode = (0.1, 0, 0)  # Destacar el porcentaje de "Presente"
        
        if total > 0:
            ax2.pie(values, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
            ax2.set_title(f"Porcentaje de Asistencia: {attendance_percentage:.1f}%")
        else:
            ax2.text(0.5, 0.5, "Sin datos de asistencia", ha="center", va="center")
            ax2.set_title("Porcentaje de Asistencia")
            
        ax2.axis("equal")  # Asegura que el gráfico circular sea un círculo
        
        # Ajustar layout
        fig.tight_layout()
        
        # Integrar gráfico en tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def logout(self):
        """Cerrar la sesión del tutor y volver a la pantalla de login"""
        from login import LoginScreen
        LoginScreen(self.root)
