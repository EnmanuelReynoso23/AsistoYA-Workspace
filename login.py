import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
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
        self.create_login_interface()

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
        self.password_entry.insert(0, "Contraseña")
        self.password_entry.configure(show="")
        self.password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.password_entry, "Contraseña", True))
        self.password_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.password_entry, "Contraseña"))
        
        # Remember me checkbox
        self.remember_var = ttk.BooleanVar()
        remember_check = ttk.Checkbutton(form_frame, text="Recordarme", 
                                       variable=self.remember_var, bootstyle="round-toggle")
        remember_check.pack(anchor="w", pady=10)
        
        # Login button
        login_button = ttk.Button(form_frame, text="Iniciar Sesión", 
                                bootstyle="primary", width=20,
                                command=self.process_admin_login)
        login_button.pack(pady=15)
        
        # Tutor access link
        tutor_link = ttk.Label(form_frame, text="¿Es usted tutor? Ingrese con código de acceso",
                             cursor="hand2", bootstyle="primary")
        tutor_link.pack(pady=5)
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
