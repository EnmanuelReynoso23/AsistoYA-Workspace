import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from user_interface import UserInterface
from database import Database
from security import Security

class AsistoYaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asisto Ya")
        self.database = Database()
        self.security = Security()
        self.user_interface = UserInterface(self.root, self.database, self.security)
        self.create_login_screen()

    def create_login_screen(self):
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(pady=20)

        ttk.Label(self.login_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(self.login_frame, text="Password").grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = ttk.Entry(self.login_frame)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.security.authenticate(username, password):
            self.login_frame.destroy()
            self.user_interface.load_main_interface()
        else:
            ttk.messagebox.showerror("Login Failed", "Invalid username or password")

    def start_attendance_session(self):
        self.user_interface.start_attendance_session()

    def stop_attendance_session(self):
        self.user_interface.stop_attendance_session()

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = AsistoYaApp(root)
    root.mainloop()
