import json
import os
import time
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class RegistrationManager:
    def __init__(self, security, school_manager):
        self.security = security
        self.school_manager = school_manager
        self.data_dir = "data"
        
    def get_pending_registrations(self):
        """Get all pending registrations"""
        pending = {
            'students': [],
            'professors': [],
            'directors': []
        }
        
        # Load student registrations
        student_file = os.path.join(self.data_dir, "student_registrations.json")
        if os.path.exists(student_file):
            with open(student_file, 'r') as f:
                students = json.load(f)
                pending['students'] = [s for s in students if s.get('status') == 'pending']
        
        # Load professor registrations
        professor_file = os.path.join(self.data_dir, "professor_registrations.json")
        if os.path.exists(professor_file):
            with open(professor_file, 'r') as f:
                professors = json.load(f)
                pending['professors'] = [p for p in professors if p.get('status') == 'pending']
        
        # Load director registrations
        director_file = os.path.join(self.data_dir, "director_registrations.json")
        if os.path.exists(director_file):
            with open(director_file, 'r') as f:
                directors = json.load(f)
                pending['directors'] = [d for d in directors if d.get('status') == 'pending']
        
        return pending
    
    def approve_student_registration(self, registration):
        """Approve a student registration"""
        try:
            # Create student in the school management system
            student = self.school_manager.register_student(
                registration['name'],
                registration['surname'], 
                registration['email']
            )
            
            # Add guardian contact if provided
            if registration.get('guardian'):
                student.add_guardian_contact(
                    "Guardian",
                    registration['guardian'],
                    registration.get('phone', '')
                )
            
            # Update registration status
            self._update_registration_status('student_registrations.json', registration, 'approved')
            
            return True, f"Estudiante {registration['name']} {registration['surname']} aprobado con código: {student.code}"
            
        except Exception as e:
            return False, f"Error al aprobar estudiante: {str(e)}"
    
    def approve_professor_registration(self, registration):
        """Approve a professor registration"""
        try:
            # Create professor in the school management system
            professor = self.school_manager.register_professor(
                registration['name'],
                registration['surname'],
                registration['email']
            )
            
            # Add professor credentials to security system
            self.security.test_users[registration['username']] = registration['password']
            
            # Update registration status
            self._update_registration_status('professor_registrations.json', registration, 'approved')
            
            return True, f"Profesor {registration['name']} {registration['surname']} aprobado con código: {professor.code}"
            
        except Exception as e:
            return False, f"Error al aprobar profesor: {str(e)}"
    
    def approve_director_registration(self, registration):
        """Approve a director registration"""
        try:
            # Add director credentials to security system with admin privileges
            self.security.test_users[registration['username']] = registration['password']
            
            # Update registration status
            self._update_registration_status('director_registrations.json', registration, 'approved')
            
            return True, f"Director {registration['name']} {registration['surname']} aprobado"
            
        except Exception as e:
            return False, f"Error al aprobar director: {str(e)}"
    
    def reject_registration(self, registration_type, registration):
        """Reject a registration"""
        try:
            file_map = {
                'student': 'student_registrations.json',
                'professor': 'professor_registrations.json', 
                'director': 'director_registrations.json'
            }
            
            self._update_registration_status(file_map[registration_type], registration, 'rejected')
            return True, f"Registro de {registration['name']} {registration['surname']} rechazado"
            
        except Exception as e:
            return False, f"Error al rechazar registro: {str(e)}"
    
    def _update_registration_status(self, filename, target_registration, new_status):
        """Update registration status in file"""
        file_path = os.path.join(self.data_dir, filename)
        
        # Load existing registrations
        registrations = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                registrations = json.load(f)
        
        # Find and update the target registration
        for reg in registrations:
            if (reg['email'] == target_registration['email'] and 
                reg['registration_date'] == target_registration['registration_date']):
                reg['status'] = new_status
                reg['processed_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
                break
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(registrations, f, indent=2)

class RegistrationWindow:
    def __init__(self, parent, registration_manager):
        self.parent = parent
        self.registration_manager = registration_manager
        self.window = ttk.Toplevel(parent)
        self.window.title("Gestión de Registros")
        self.window.geometry("900x600")
        self.window.grab_set()  # Make window modal
        
        self.create_interface()
        self.load_pending_registrations()
        
    def create_interface(self):
        """Create the registration management interface"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Gestión de Solicitudes de Registro", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Notebook for different registration types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Student registrations tab
        self.student_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.student_frame, text="Estudiantes")
        self.create_registration_tab(self.student_frame, "student")
        
        # Professor registrations tab
        self.professor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.professor_frame, text="Profesores")
        self.create_registration_tab(self.professor_frame, "professor")
        
        # Director registrations tab
        self.director_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.director_frame, text="Directores")
        self.create_registration_tab(self.director_frame, "director")
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Cerrar", 
                             bootstyle="secondary",
                             command=self.window.destroy)
        close_btn.pack(pady=10)
    
    def create_registration_tab(self, parent, reg_type):
        """Create a tab for managing registrations of a specific type"""
        # Container
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=BOTH, expand=True)
        
        # Treeview for registrations
        columns = {
            'student': ("Nombre", "Apellido", "Email", "Teléfono", "Tutor", "Fecha"),
            'professor': ("Nombre", "Apellido", "Email", "Departamento", "Usuario", "Fecha"),
            'director': ("Nombre", "Apellido", "Email", "Institución", "Usuario", "Fecha")
        }
        
        tree = ttk.Treeview(container, columns=columns[reg_type], show="headings", height=15)
        
        # Configure column headings
        for col in columns[reg_type]:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Store reference to tree
        setattr(self, f"{reg_type}_tree", tree)
        
        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=X, pady=10)
        
        # Approve button
        approve_btn = ttk.Button(button_frame, text="Aprobar", 
                               bootstyle="success",
                               command=lambda: self.approve_registration(reg_type))
        approve_btn.pack(side=LEFT, padx=5)
        
        # Reject button
        reject_btn = ttk.Button(button_frame, text="Rechazar", 
                              bootstyle="danger",
                              command=lambda: self.reject_registration(reg_type))
        reject_btn.pack(side=LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(button_frame, text="Actualizar", 
                               bootstyle="info",
                               command=self.load_pending_registrations)
        refresh_btn.pack(side=LEFT, padx=5)
    
    def load_pending_registrations(self):
        """Load pending registrations into the treeviews"""
        pending = self.registration_manager.get_pending_registrations()
        
        # Clear existing items
        for reg_type in ['student', 'professor', 'director']:
            tree = getattr(self, f"{reg_type}_tree")
            for item in tree.get_children():
                tree.delete(item)
        
        # Load student registrations
        for student in pending['students']:
            self.student_tree.insert("", "end", values=(
                student['name'],
                student['surname'],
                student['email'],
                student.get('phone', ''),
                student.get('guardian', ''),
                student['registration_date']
            ))
        
        # Load professor registrations
        for professor in pending['professors']:
            self.professor_tree.insert("", "end", values=(
                professor['name'],
                professor['surname'],
                professor['email'],
                professor.get('department', ''),
                professor['username'],
                professor['registration_date']
            ))
        
        # Load director registrations
        for director in pending['directors']:
            self.director_tree.insert("", "end", values=(
                director['name'],
                director['surname'],
                director['email'],
                director.get('institution', ''),
                director['username'],
                director['registration_date']
            ))
    
    def approve_registration(self, reg_type):
        """Approve the selected registration"""
        tree = getattr(self, f"{reg_type}_tree")
        selection = tree.selection()
        
        if not selection:
            messagebox.showwarning("Selección requerida", 
                                 "Por favor seleccione un registro para aprobar.")
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Find the registration data
        pending = self.registration_manager.get_pending_registrations()
        registration = None
        
        reg_list = pending[f"{reg_type}s"]
        for reg in reg_list:
            if (reg['name'] == values[0] and 
                reg['surname'] == values[1] and 
                reg['email'] == values[2]):
                registration = reg
                break
        
        if not registration:
            messagebox.showerror("Error", "No se pudo encontrar el registro seleccionado.")
            return
        
        # Approve the registration
        if reg_type == 'student':
            success, message = self.registration_manager.approve_student_registration(registration)
        elif reg_type == 'professor':
            success, message = self.registration_manager.approve_professor_registration(registration)
        elif reg_type == 'director':
            success, message = self.registration_manager.approve_director_registration(registration)
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.load_pending_registrations()
        else:
            messagebox.showerror("Error", message)
    
    def reject_registration(self, reg_type):
        """Reject the selected registration"""
        tree = getattr(self, f"{reg_type}_tree")
        selection = tree.selection()
        
        if not selection:
            messagebox.showwarning("Selección requerida", 
                                 "Por favor seleccione un registro para rechazar.")
            return
        
        # Confirm rejection
        if not messagebox.askyesno("Confirmar rechazo", 
                                  "¿Está seguro de que desea rechazar este registro?"):
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Find the registration data
        pending = self.registration_manager.get_pending_registrations()
        registration = None
        
        reg_list = pending[f"{reg_type}s"]
        for reg in reg_list:
            if (reg['name'] == values[0] and 
                reg['surname'] == values[1] and 
                reg['email'] == values[2]):
                registration = reg
                break
        
        if not registration:
            messagebox.showerror("Error", "No se pudo encontrar el registro seleccionado.")
            return
        
        # Reject the registration
        success, message = self.registration_manager.reject_registration(reg_type, registration)
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.load_pending_registrations()
        else:
            messagebox.showerror("Error", message)
