import tkinter as tk
from tkinter import messagebox
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
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.login_frame, text="Password").grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(self.login_frame)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.security.authenticate(username, password):
            self.login_frame.destroy()
            self.user_interface.load_main_interface()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def start_attendance_session(self):
        self.user_interface.start_attendance_session()

    def stop_attendance_session(self):
        self.user_interface.stop_attendance_session()

if __name__ == "__main__":
    root = tk.Tk()
    app = AsistoYaApp(root)
    root.mainloop()
