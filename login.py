import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

class LoginScreen:
    def __init__(self, root, security, on_login_success):
        self.root = root
        self.security = security
        self.on_login_success = on_login_success
        self.create_login_interface()

    def create_login_interface(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create login frame
        self.login_frame = ttk.Frame(self.root, padding=20)
        self.login_frame.pack(fill=BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.login_frame, text="Asisto Ya", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        # Username
        username_frame = ttk.Frame(self.login_frame)
        username_frame.pack(fill=X, pady=10)
        
        username_label = ttk.Label(username_frame, text="Usuario:", width=10)
        username_label.pack(side=LEFT, padx=5)
        
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=LEFT, fill=X, expand=True)
        
        # Password
        password_frame = ttk.Frame(self.login_frame)
        password_frame.pack(fill=X, pady=10)
        
        password_label = ttk.Label(password_frame, text="Contraseña:", width=10)
        password_label.pack(side=LEFT, padx=5)
        
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=LEFT, fill=X, expand=True)
        
        # Login button
        button_frame = ttk.Frame(self.login_frame)
        button_frame.pack(pady=20)
        
        login_button = ttk.Button(button_frame, text="Iniciar Sesión", command=self.login, bootstyle=SUCCESS)
        login_button.pack(side=LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.root.quit, bootstyle=DANGER)
        cancel_button.pack(side=LEFT, padx=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return
            
        # Validate credentials with security module
        if self.security.authenticate(username, password):
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
