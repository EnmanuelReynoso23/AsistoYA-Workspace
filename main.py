import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from user_interface import UserInterface
# from database import Database
from security import Security
from login import LoginScreen

class AsistoYaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asisto Ya")
        # self.database = Database(
        #     cred_path="firebase_service_account.json",
        #     db_url="https://asistoya-demo-default-rtdb.firebaseio.com/"
        # )
        self.security = Security()
        self.user_interface = UserInterface(self.root, None, self.security)
        self.create_login_screen()

    def create_login_screen(self):
        self.login_screen = LoginScreen(self.root, self.security, self.on_login_success)

    def on_login_success(self):
        self.user_interface.load_main_interface()

    def start_attendance_session(self):
        self.user_interface.start_attendance_session()

    def stop_attendance_session(self):
        self.user_interface.stop_attendance_session()

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = AsistoYaApp(root)
    root.mainloop()
