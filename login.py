import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
import os
from PIL import Image, ImageTk
import json
import time

class LoginScreen:
    def __init__(self, root, security, on_login_success, on_tutor_login_success=None):
        self.root = root
        self.security = security
        self.on_login_success = on_login_success
        self.on_tutor_login_success = on_tutor_login_success or self.default_tutor_login
        self.failed_attempts = 0
        self.login_blocked_until = None
        self.saved_credentials_file = "data/saved_credentials.json"
        self.load_saved_credentials()
        self.create_login_interface()

    def load_saved_credentials(self):
        """Load saved credentials from file"""
        self.saved_credentials = {}
        try:
            if os.path.exists(self.saved_credentials_file):
                with open(self.saved_credentials_file, 'r') as f:
                    self.saved_credentials = json.load(f)
        except Exception as e:
            print(f"Error loading saved credentials: {e}")
            self.saved_credentials = {}

    def save_credentials(self, username, password):
        """Save credentials to file"""
        try:
            os.makedirs("data", exist_ok=True)
            self.saved_credentials[username] = password
            with open(self.saved_credentials_file, 'w') as f:
                json.dump(self.saved_credentials, f)
        except Exception as e:
            print(f"Error saving credentials: {e}")

    def remove_saved_credentials(self, username):
        """Remove saved credentials for a user"""
        try:
            if username in self.saved_credentials:
                del self.saved_credentials[username]
                with open(self.saved_credentials_file, 'w') as f:
                    json.dump(self.saved_credentials, f)
        except Exception as e:
            print(f"Error removing saved credentials: {e}")

    def create_login_interface(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Set window size
        window_width = 800
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main container with two sides
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Left side - Logo/Image area (blue background)
        left_frame = ttk.Frame(main_frame, bootstyle="primary")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Try to load logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            try:
                original_img = Image.open(logo_path)
                resized_img = original_img.resize((300, 300), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(resized_img)
                logo_label = ttk.Label(left_frame, image=self.logo_img, bootstyle="primary")
                logo_label.pack(pady=50)
            except Exception as e:
                print(f"Error loading logo: {e}")
                self.create_default_logo(left_frame)
        else:
            self.create_default_logo(left_frame)
        
        # Add app name
        app_name = ttk.Label(left_frame, text="AsistoYA", 
                           font=("Arial", 28, "bold"), bootstyle="primary-inverse")
        app_name.pack(pady=10)
        
        app_slogan = ttk.Label(left_frame, 
                             text="Sistema de Asistencia con Reconocimiento Facial",
                             font=("Arial", 12), bootstyle="primary-inverse")
        app_slogan.pack()
        
        # Right side - Login form
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Show admin login by default
        self.show_admin_login()
        
    def create_default_logo(self, parent):
        """Create a placeholder logo if no logo image is available"""
        logo_frame = ttk.Frame(parent, width=200, height=200)
        logo_frame.pack(pady=50)
        
        # Create circular placeholder
        canvas = ttk.Canvas(logo_frame, width=200, height=200, highlightthickness=0)
        canvas.pack()
          # Draw a circular placeholder with school icon
        canvas.create_oval(10, 10, 190, 190, fill="white", outline="white")
        canvas.create_text(100, 100, text="A", font=("Arial", 80, "bold"), fill="#0063B1")
        
    def show_admin_login(self):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        
        # Container for login form with padding
        form_frame = ttk.Frame(self.right_frame, padding=30)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Login form title
        login_title = ttk.Label(form_frame, text="Iniciar Sesión", font=("Arial", 20, "bold"))
        login_title.pack(pady=(20, 30))
        
        # Username field with icon
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=X, pady=10)
        
        username_icon = ttk.Label(username_frame, text="👤", font=("Arial", 14))
        username_icon.pack(side=LEFT, padx=(0, 10))
        
        self.username_var = ttk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.username_var,
                                 font=("Arial", 12), width=30)
        username_entry.pack(fill=X)
        
        # Load saved username if available
        if self.saved_credentials:
            first_user = next(iter(self.saved_credentials))
            username_entry.insert(0, first_user)
        else:
            username_entry.insert(0, "Usuario")
        
        username_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(username_entry, "Usuario"))
        username_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(username_entry, "Usuario"))
        
        # Password field with icon
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=X, pady=10)
        
        password_icon = ttk.Label(password_frame, text="🔒", font=("Arial", 14))
        password_icon.pack(side=LEFT, padx=(0, 10))
        
        self.password_var = ttk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var,
                                    font=("Arial", 12), width=30, show="•")
        self.password_entry.pack(fill=X)
        
        # Load saved password if remember me was checked
        if self.saved_credentials and self.username_var.get() in self.saved_credentials:
            self.password_entry.insert(0, self.saved_credentials[self.username_var.get()])
        else:
            self.password_entry.insert(0, "Contraseña")
            self.password_entry.configure(show="")
        
        self.password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.password_entry, "Contraseña", True))
        self.password_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.password_entry, "Contraseña"))
        
        # Remember me checkbox
        self.remember_var = ttk.BooleanVar()
        # Check remember me if credentials are saved
        if self.saved_credentials and self.username_var.get() in self.saved_credentials:
            self.remember_var.set(True)
            
        remember_check = ttk.Checkbutton(form_frame, text="Recordarme", 
                                       variable=self.remember_var, bootstyle="round-toggle")
        remember_check.pack(anchor="w", pady=10)
        
        # Login button
        login_button = ttk.Button(form_frame, text="Iniciar Sesión", 
                                bootstyle="primary", width=20,
                                command=self.process_admin_login)
        login_button.pack(pady=15)
        
        # Registration buttons section
        register_frame = ttk.Frame(form_frame)
        register_frame.pack(fill=X, pady=10)
        
        register_label = ttk.Label(register_frame, text="¿No tienes cuenta?", 
                                 font=("Arial", 10))
        register_label.pack(pady=(0, 5))
        
        # Student registration button
        register_student_btn = ttk.Button(register_frame, text="Registrar Estudiante", 
                                        bootstyle="info-outline", width=18,
                                        command=self.show_student_registration)
        register_student_btn.pack(pady=2)
        
        # Professor registration button
        register_professor_btn = ttk.Button(register_frame, text="Registrar Profesor", 
                                          bootstyle="success-outline", width=18,
                                          command=self.show_professor_registration)
        register_professor_btn.pack(pady=2)
        
        # Director registration button
        register_director_btn = ttk.Button(register_frame, text="Registrar Director", 
                                         bootstyle="warning-outline", width=18,
                                         command=self.show_director_registration)
        register_director_btn.pack(pady=2)
        
        # Tutor access link
        tutor_link = ttk.Label(form_frame, text="¿Es usted tutor? Ingrese con código de acceso",
                             cursor="hand2", bootstyle="primary")
        tutor_link.pack(pady=10)
        tutor_link.bind("<Button-1>", lambda e: self.show_tutor_login())
        
        # Error message area
        self.error_var = ttk.StringVar()
        self.error_label = ttk.Label(form_frame, textvariable=self.error_var,
                                  bootstyle="danger")
        self.error_label.pack(pady=10)
        
        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self.process_admin_login())
        username_entry.bind("<Return>", lambda e: self.password_entry.focus())
    
    def show_tutor_login(self):
        """Mostrar la interfaz de inicio de sesión para tutores"""
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        
        # Container for login form with padding
        form_frame = ttk.Frame(self.right_frame, padding=30)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Login form title
        login_title = ttk.Label(form_frame, text="Acceso para Tutores", font=("Arial", 20, "bold"))
        login_title.pack(pady=(20, 30))
        
        # Description
        description = ttk.Label(form_frame, 
                             text="Ingrese el código de acceso proporcionado por la institución",
                             wraplength=300, justify="center")
        description.pack(pady=10)
        
        # Access code field with icon
        code_frame = ttk.Frame(form_frame)
        code_frame.pack(fill=X, pady=20)
        
        code_icon = ttk.Label(code_frame, text="🔑", font=("Arial", 14))
        code_icon.pack(side=LEFT, padx=(0, 10))
        
        self.access_code_var = ttk.StringVar()
        self.access_code_entry = ttk.Entry(code_frame, textvariable=self.access_code_var,
                                      font=("Arial", 14), width=25, justify="center")
        self.access_code_entry.pack(fill=X)
        self.access_code_entry.focus()
        
        # Access button
        access_button = ttk.Button(form_frame, text="Acceder", 
                                bootstyle="primary", width=20,
                                command=self.process_tutor_login)
        access_button.pack(pady=25)
        
        # Back to admin login link
        admin_link = ttk.Label(form_frame, text="Volver al inicio de sesión administrativo",
                             cursor="hand2", bootstyle="primary")
        admin_link.pack(pady=10)
        admin_link.bind("<Button-1>", lambda e: self.show_admin_login())
        
        # Error message area
        self.error_var = ttk.StringVar()
        self.error_label = ttk.Label(form_frame, textvariable=self.error_var,
                                  bootstyle="danger")
        self.error_label.pack(pady=10)
        
        # Bind Enter key to access
        self.access_code_entry.bind("<Return>", lambda e: self.process_tutor_login())
        
    def process_tutor_login(self):
        """Procesar el inicio de sesión de un tutor con código de acceso"""
        access_code = self.access_code_var.get().strip().upper()
        
        if not access_code:
            self.error_var.set("Debe ingresar un código de acceso")
            return
        
        # Validar el código de acceso
        code_data = self.security.validate_tutor_access_code(access_code)
        
        if code_data is None:
            self.error_var.set("Código de acceso inválido o expirado")
            return
        
        # Código válido, proceder con inicio de sesión
        self.error_var.set("")
        self.on_tutor_login_success(code_data)
    
    def clear_placeholder(self, entry, placeholder_text, is_password=False):
        if entry.get() == placeholder_text:
            entry.delete(0, 'end')
            if is_password:
                entry.configure(show="•")
    
    def restore_placeholder(self, entry, placeholder_text):
        if entry.get() == "":
            entry.insert(0, placeholder_text)
            if placeholder_text == "Contraseña" and entry.get() == "Contraseña":
                entry.configure(show="")
      def process_admin_login(self):
        """Process admin login attempt"""
        # Check if login is temporarily blocked
        if self.login_blocked_until and time.time() < self.login_blocked_until:
            remaining = int(self.login_blocked_until - time.time())
            self.error_var.set(f"Demasiados intentos fallidos. Intente de nuevo en {remaining} segundos.")
            return
            
        username = self.username_var.get()
        password = self.password_var.get()
        
        # Handle placeholder cases
        if username == "Usuario" or not username:
            self.error_var.set("Por favor ingrese su nombre de usuario")
            return
            
        if password == "Contraseña" or not password:
            self.error_var.set("Por favor ingrese su contraseña")
            return
            
        # Authenticate user
        if self.security.authenticate(username, password):
            self.error_var.set("")
            self.failed_attempts = 0
            
            # Handle remember me functionality
            if self.remember_var.get():
                self.save_credentials(username, password)
                messagebox.showinfo("Credenciales Guardadas", 
                                  "Sus credenciales han sido guardadas para futuros inicios de sesión.")
            else:
                # Remove saved credentials if remember me is unchecked
                self.remove_saved_credentials(username)
            
            self.on_login_success(username)
        else:
            self.failed_attempts += 1
            
            # After 3 failed attempts, block login temporarily
            if self.failed_attempts >= 3:
                block_time = 60  # seconds
                self.login_blocked_until = time.time() + block_time
                self.error_var.set(f"Demasiados intentos fallidos. Intente de nuevo en {block_time} segundos.")
            else:
                remaining = 3 - self.failed_attempts
                self.error_var.set(f"Nombre de usuario o contraseña incorrectos. {remaining} intentos restantes.")
    
    def default_tutor_login(self, tutor_data):
        """Default handler for tutor login if no custom handler provided"""
        messagebox.showinfo("Acceso de tutor", 
                           f"Acceso exitoso como tutor para estudiante: {tutor_data['student_id']}")
        
    def generate_access_code(self, student_id, course_id=None):
        """Generate access code for a tutor"""
        return self.security.generate_tutor_access_code(student_id, course_id)

    def show_student_registration(self):
        """Show student registration form"""
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        # Container for registration form with padding
        form_frame = ttk.Frame(self.right_frame, padding=30)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Registration form title
        title = ttk.Label(form_frame, text="Registro de Estudiante", font=("Arial", 20, "bold"))
        title.pack(pady=(20, 30))
        
        # Name field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=X, pady=5)
        ttk.Label(name_frame, text="Nombre:", font=("Arial", 10)).pack(anchor="w")
        self.reg_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.reg_name_var, font=("Arial", 12))
        name_entry.pack(fill=X)
        
        # Surname field
        surname_frame = ttk.Frame(form_frame)
        surname_frame.pack(fill=X, pady=5)
        ttk.Label(surname_frame, text="Apellido:", font=("Arial", 10)).pack(anchor="w")
        self.reg_surname_var = ttk.StringVar()
        surname_entry = ttk.Entry(surname_frame, textvariable=self.reg_surname_var, font=("Arial", 12))
        surname_entry.pack(fill=X)
        
        # Email field
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=X, pady=5)
        ttk.Label(email_frame, text="Email:", font=("Arial", 10)).pack(anchor="w")
        self.reg_email_var = ttk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.reg_email_var, font=("Arial", 12))
        email_entry.pack(fill=X)
        
        # Phone field
        phone_frame = ttk.Frame(form_frame)
        phone_frame.pack(fill=X, pady=5)
        ttk.Label(phone_frame, text="Teléfono:", font=("Arial", 10)).pack(anchor="w")
        self.reg_phone_var = ttk.StringVar()
        phone_entry = ttk.Entry(phone_frame, textvariable=self.reg_phone_var, font=("Arial", 12))
        phone_entry.pack(fill=X)
        
        # Guardian contact
        guardian_frame = ttk.Frame(form_frame)
        guardian_frame.pack(fill=X, pady=5)
        ttk.Label(guardian_frame, text="Contacto del Tutor:", font=("Arial", 10)).pack(anchor="w")
        self.reg_guardian_var = ttk.StringVar()
        guardian_entry = ttk.Entry(guardian_frame, textvariable=self.reg_guardian_var, font=("Arial", 12))
        guardian_entry.pack(fill=X)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=X, pady=20)
        
        # Register button
        register_btn = ttk.Button(button_frame, text="Registrar Estudiante", 
                                bootstyle="success", width=20,
                                command=self.process_student_registration)
        register_btn.pack(side=LEFT, padx=(0, 10))
        
        # Back button
        back_btn = ttk.Button(button_frame, text="Volver", 
                            bootstyle="secondary", width=15,
                            command=self.show_admin_login)
        back_btn.pack(side=LEFT)
        
        # Error/Success message area
        self.reg_error_var = ttk.StringVar()
        self.reg_error_label = ttk.Label(form_frame, textvariable=self.reg_error_var,
                                      bootstyle="info")
        self.reg_error_label.pack(pady=10)

    def show_professor_registration(self):
        """Show professor registration form"""
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        # Container for registration form with padding
        form_frame = ttk.Frame(self.right_frame, padding=30)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Registration form title
        title = ttk.Label(form_frame, text="Registro de Profesor", font=("Arial", 20, "bold"))
        title.pack(pady=(20, 30))
        
        # Name field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=X, pady=5)
        ttk.Label(name_frame, text="Nombre:", font=("Arial", 10)).pack(anchor="w")
        self.reg_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.reg_name_var, font=("Arial", 12))
        name_entry.pack(fill=X)
        
        # Surname field
        surname_frame = ttk.Frame(form_frame)
        surname_frame.pack(fill=X, pady=5)
        ttk.Label(surname_frame, text="Apellido:", font=("Arial", 10)).pack(anchor="w")
        self.reg_surname_var = ttk.StringVar()
        surname_entry = ttk.Entry(surname_frame, textvariable=self.reg_surname_var, font=("Arial", 12))
        surname_entry.pack(fill=X)
        
        # Email field
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=X, pady=5)
        ttk.Label(email_frame, text="Email:", font=("Arial", 10)).pack(anchor="w")
        self.reg_email_var = ttk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.reg_email_var, font=("Arial", 12))
        email_entry.pack(fill=X)
        
        # Department field
        dept_frame = ttk.Frame(form_frame)
        dept_frame.pack(fill=X, pady=5)
        ttk.Label(dept_frame, text="Departamento:", font=("Arial", 10)).pack(anchor="w")
        self.reg_dept_var = ttk.StringVar()
        dept_entry = ttk.Entry(dept_frame, textvariable=self.reg_dept_var, font=("Arial", 12))
        dept_entry.pack(fill=X)
        
        # Username field
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=X, pady=5)
        ttk.Label(username_frame, text="Nombre de Usuario:", font=("Arial", 10)).pack(anchor="w")
        self.reg_username_var = ttk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.reg_username_var, font=("Arial", 12))
        username_entry.pack(fill=X)
        
        # Password field
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=X, pady=5)
        ttk.Label(password_frame, text="Contraseña:", font=("Arial", 10)).pack(anchor="w")
        self.reg_password_var = ttk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.reg_password_var, 
                                 font=("Arial", 12), show="•")
        password_entry.pack(fill=X)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=X, pady=20)
        
        # Register button
        register_btn = ttk.Button(button_frame, text="Registrar Profesor", 
                                bootstyle="success", width=20,
                                command=self.process_professor_registration)
        register_btn.pack(side=LEFT, padx=(0, 10))
        
        # Back button
        back_btn = ttk.Button(button_frame, text="Volver", 
                            bootstyle="secondary", width=15,
                            command=self.show_admin_login)
        back_btn.pack(side=LEFT)
        
        # Error/Success message area
        self.reg_error_var = ttk.StringVar()
        self.reg_error_label = ttk.Label(form_frame, textvariable=self.reg_error_var,
                                      bootstyle="info")
        self.reg_error_label.pack(pady=10)

    def show_director_registration(self):
        """Show director registration form"""
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        # Container for registration form with padding
        form_frame = ttk.Frame(self.right_frame, padding=30)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Registration form title
        title = ttk.Label(form_frame, text="Registro de Director", font=("Arial", 20, "bold"))
        title.pack(pady=(20, 30))
        
        # Name field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=X, pady=5)
        ttk.Label(name_frame, text="Nombre:", font=("Arial", 10)).pack(anchor="w")
        self.reg_name_var = ttk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.reg_name_var, font=("Arial", 12))
        name_entry.pack(fill=X)
        
        # Surname field
        surname_frame = ttk.Frame(form_frame)
        surname_frame.pack(fill=X, pady=5)
        ttk.Label(surname_frame, text="Apellido:", font=("Arial", 10)).pack(anchor="w")
        self.reg_surname_var = ttk.StringVar()
        surname_entry = ttk.Entry(surname_frame, textvariable=self.reg_surname_var, font=("Arial", 12))
        surname_entry.pack(fill=X)
        
        # Email field
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=X, pady=5)
        ttk.Label(email_frame, text="Email:", font=("Arial", 10)).pack(anchor="w")
        self.reg_email_var = ttk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.reg_email_var, font=("Arial", 12))
        email_entry.pack(fill=X)
        
        # Institution field
        institution_frame = ttk.Frame(form_frame)
        institution_frame.pack(fill=X, pady=5)
        ttk.Label(institution_frame, text="Institución:", font=("Arial", 10)).pack(anchor="w")
        self.reg_institution_var = ttk.StringVar()
        institution_entry = ttk.Entry(institution_frame, textvariable=self.reg_institution_var, font=("Arial", 12))
        institution_entry.pack(fill=X)
        
        # Username field
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=X, pady=5)
        ttk.Label(username_frame, text="Nombre de Usuario:", font=("Arial", 10)).pack(anchor="w")
        self.reg_username_var = ttk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.reg_username_var, font=("Arial", 12))
        username_entry.pack(fill=X)
        
        # Password field
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=X, pady=5)
        ttk.Label(password_frame, text="Contraseña:", font=("Arial", 10)).pack(anchor="w")
        self.reg_password_var = ttk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.reg_password_var, 
                                 font=("Arial", 12), show="•")
        password_entry.pack(fill=X)
        
        # Authority Code field (for verification)
        auth_frame = ttk.Frame(form_frame)
        auth_frame.pack(fill=X, pady=5)
        ttk.Label(auth_frame, text="Código de Autorización:", font=("Arial", 10)).pack(anchor="w")
        self.reg_auth_var = ttk.StringVar()
        auth_entry = ttk.Entry(auth_frame, textvariable=self.reg_auth_var, font=("Arial", 12))
        auth_entry.pack(fill=X)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=X, pady=20)
        
        # Register button
        register_btn = ttk.Button(button_frame, text="Registrar Director", 
                                bootstyle="success", width=20,
                                command=self.process_director_registration)
        register_btn.pack(side=LEFT, padx=(0, 10))
        
        # Back button
        back_btn = ttk.Button(button_frame, text="Volver", 
                            bootstyle="secondary", width=15,
                            command=self.show_admin_login)
        back_btn.pack(side=LEFT)
        
        # Error/Success message area
        self.reg_error_var = ttk.StringVar()
        self.reg_error_label = ttk.Label(form_frame, textvariable=self.reg_error_var,
                                      bootstyle="info")
        self.reg_error_label.pack(pady=10)

    def process_student_registration(self):
        """Process student registration"""
        name = self.reg_name_var.get().strip()
        surname = self.reg_surname_var.get().strip()
        email = self.reg_email_var.get().strip()
        phone = self.reg_phone_var.get().strip()
        guardian = self.reg_guardian_var.get().strip()
        
        # Validation
        if not all([name, surname, email]):
            self.reg_error_var.set("Por favor complete todos los campos requeridos.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        # Email validation
        if "@" not in email or "." not in email:
            self.reg_error_var.set("Por favor ingrese un email válido.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        try:
            # Save student registration data to file
            os.makedirs("data", exist_ok=True)
            registration_file = "data/student_registrations.json"
            
            # Load existing registrations
            registrations = []
            if os.path.exists(registration_file):
                with open(registration_file, 'r') as f:
                    registrations = json.load(f)
            
            # Check if email already exists
            for reg in registrations:
                if reg['email'] == email:
                    self.reg_error_var.set("Ya existe un estudiante registrado con este email.")
                    self.reg_error_label.config(bootstyle="danger")
                    return
            
            # Add new registration
            new_registration = {
                'name': name,
                'surname': surname,
                'email': email,
                'phone': phone,
                'guardian': guardian,
                'registration_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'pending'
            }
            
            registrations.append(new_registration)
            
            # Save to file
            with open(registration_file, 'w') as f:
                json.dump(registrations, f, indent=2)
            
            self.reg_error_var.set("¡Registro exitoso! Su solicitud está siendo procesada.")
            self.reg_error_label.config(bootstyle="success")
            
            # Clear form
            self.reg_name_var.set("")
            self.reg_surname_var.set("")
            self.reg_email_var.set("")
            self.reg_phone_var.set("")
            self.reg_guardian_var.set("")
            
        except Exception as e:
            self.reg_error_var.set(f"Error en el registro: {str(e)}")
            self.reg_error_label.config(bootstyle="danger")

    def process_professor_registration(self):
        """Process professor registration"""
        name = self.reg_name_var.get().strip()
        surname = self.reg_surname_var.get().strip()
        email = self.reg_email_var.get().strip()
        department = self.reg_dept_var.get().strip()
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get().strip()
        
        # Validation
        if not all([name, surname, email, username, password]):
            self.reg_error_var.set("Por favor complete todos los campos requeridos.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        # Email validation
        if "@" not in email or "." not in email:
            self.reg_error_var.set("Por favor ingrese un email válido.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        # Password validation
        if len(password) < 6:
            self.reg_error_var.set("La contraseña debe tener al menos 6 caracteres.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        try:
            # Save professor registration data to file
            os.makedirs("data", exist_ok=True)
            registration_file = "data/professor_registrations.json"
            
            # Load existing registrations
            registrations = []
            if os.path.exists(registration_file):
                with open(registration_file, 'r') as f:
                    registrations = json.load(f)
            
            # Check if username or email already exists
            for reg in registrations:
                if reg['username'] == username:
                    self.reg_error_var.set("Ya existe un profesor registrado con este nombre de usuario.")
                    self.reg_error_label.config(bootstyle="danger")
                    return
                if reg['email'] == email:
                    self.reg_error_var.set("Ya existe un profesor registrado con este email.")
                    self.reg_error_label.config(bootstyle="danger")
                    return
            
            # Hash password
            hashed_password = self.security.hash_password(password)
            
            # Add new registration
            new_registration = {
                'name': name,
                'surname': surname,
                'email': email,
                'department': department,
                'username': username,
                'password': hashed_password,
                'registration_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'pending',
                'role': 'professor'
            }
            
            registrations.append(new_registration)
            
            # Save to file
            with open(registration_file, 'w') as f:
                json.dump(registrations, f, indent=2)
            
            self.reg_error_var.set("¡Registro exitoso! Su solicitud está siendo procesada.")
            self.reg_error_label.config(bootstyle="success")
            
            # Clear form
            self.reg_name_var.set("")
            self.reg_surname_var.set("")
            self.reg_email_var.set("")
            self.reg_dept_var.set("")
            self.reg_username_var.set("")
            self.reg_password_var.set("")
            
        except Exception as e:
            self.reg_error_var.set(f"Error en el registro: {str(e)}")
            self.reg_error_label.config(bootstyle="danger")

    def process_director_registration(self):
        """Process director registration"""
        name = self.reg_name_var.get().strip()
        surname = self.reg_surname_var.get().strip()
        email = self.reg_email_var.get().strip()
        institution = self.reg_institution_var.get().strip()
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get().strip()
        auth_code = self.reg_auth_var.get().strip()
        
        # Validation
        if not all([name, surname, email, username, password, auth_code]):
            self.reg_error_var.set("Por favor complete todos los campos requeridos.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        # Email validation
        if "@" not in email or "." not in email:
            self.reg_error_var.set("Por favor ingrese un email válido.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        # Password validation
        if len(password) < 8:
            self.reg_error_var.set("La contraseña debe tener al menos 8 caracteres.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        # Authority code validation (simple check - could be enhanced)
        if auth_code != "DIRECTOR2024":
            self.reg_error_var.set("Código de autorización inválido.")
            self.reg_error_label.config(bootstyle="danger")
            return
            
        try:
            # Save director registration data to file
            os.makedirs("data", exist_ok=True)
            registration_file = "data/director_registrations.json"
            
            # Load existing registrations
            registrations = []
            if os.path.exists(registration_file):
                with open(registration_file, 'r') as f:
                    registrations = json.load(f)
            
            # Check if username or email already exists
            for reg in registrations:
                if reg['username'] == username:
                    self.reg_error_var.set("Ya existe un director registrado con este nombre de usuario.")
                    self.reg_error_label.config(bootstyle="danger")
                    return
                if reg['email'] == email:
                    self.reg_error_var.set("Ya existe un director registrado con este email.")
                    self.reg_error_label.config(bootstyle="danger")
                    return
            
            # Hash password
            hashed_password = self.security.hash_password(password)
            
            # Add new registration
            new_registration = {
                'name': name,
                'surname': surname,
                'email': email,
                'institution': institution,
                'username': username,
                'password': hashed_password,
                'registration_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'pending',
                'role': 'director'
            }
            
            registrations.append(new_registration)
            
            # Save to file
            with open(registration_file, 'w') as f:
                json.dump(registrations, f, indent=2)
            
            self.reg_error_var.set("¡Registro exitoso! Su solicitud está siendo procesada.")
            self.reg_error_label.config(bootstyle="success")
            
            # Clear form
            self.reg_name_var.set("")
            self.reg_surname_var.set("")
            self.reg_email_var.set("")
            self.reg_institution_var.set("")
            self.reg_username_var.set("")
            self.reg_password_var.set("")
            self.reg_auth_var.set("")
            
        except Exception as e:
            self.reg_error_var.set(f"Error en el registro: {str(e)}")
            self.reg_error_label.config(bootstyle="danger")
