import tkinter as tk
from tkinter import messagebox

class Help:
    def __init__(self, root):
        self.root = root
        self.create_help_interface()

    def create_help_interface(self):
        self.help_frame = tk.Frame(self.root)
        self.help_frame.pack(fill=tk.BOTH, expand=True)

        self.create_user_manual()
        self.create_about_section()

    def create_user_manual(self):
        user_manual_text = """
        User Manual:
        1. To start the application, run main.py.
        2. Login with your username and password.
        3. Use the main interface to start, pause, and stop attendance sessions.
        4. View real-time classroom feed and detected faces.
        5. Manage student attendance and send notifications.
        6. Generate and export attendance reports.
        7. Adjust application settings as needed.
        """
        self.user_manual_label = tk.Label(self.help_frame, text=user_manual_text, justify=tk.LEFT)
        self.user_manual_label.pack(pady=10)

    def create_about_section(self):
        about_text = """
        About Asisto Ya:
        Version: 1.0.0
        Contact: support@asistoya.com
        """
        self.about_label = tk.Label(self.help_frame, text=about_text, justify=tk.LEFT)
        self.about_label.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Help and Support")
    help_app = Help(root)
    root.mainloop()
