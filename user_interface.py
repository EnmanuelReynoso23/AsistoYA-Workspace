import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from camera import Camera
from attendance import AttendanceManager
from notifications import NotificationManager
from tkinter import Menu
from tkinter import messagebox
from tkinter import ttk as tk

class UserInterface:
    def __init__(self, root, database, security):
        self.root = root
        self.database = database
        self.security = security
        self.camera = Camera()
        self.attendance_manager = AttendanceManager(database)
        self.notification_manager = NotificationManager(api_url="https://api.whatsapp.com/send", api_key="YOUR_API_KEY")
        self.create_main_interface()
        self.create_tooltips()
        self.create_context_menu()

    def create_main_interface(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_camera_view()
        self.create_student_list()
        self.create_control_buttons()

    def create_camera_view(self):
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)

        self.update_camera_view()

    def update_camera_view(self):
        ret, frame = self.camera.capture.read()
        if ret:
            processed_frame = self.camera.process_frame(frame)
            self.camera_label.imgtk = processed_frame
            self.camera_label.configure(image=processed_frame)
        self.root.after(10, self.update_camera_view)

    def create_student_list(self):
        self.student_list_frame = ttk.Frame(self.main_frame)
        self.student_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.student_list = ttk.Treeview(self.student_list_frame, columns=("ID", "Name", "Status"), show="headings")
        self.student_list.heading("ID", text="ID")
        self.student_list.heading("Name", text="Name")
        self.student_list.heading("Status", text="Status")
        self.student_list.pack(fill=tk.BOTH, expand=True)

        self.load_student_list()

    def load_student_list(self):
        students = self.database.get_all_students()
        for student in students:
            self.student_list.insert("", "end", values=(student["id"], student["name"], student["status"]))

    def create_control_buttons(self):
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_button = ttk.Button(self.control_frame, text="Iniciar sesión de asistencia", command=self.start_attendance_session)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = ttk.Button(self.control_frame, text="Pausar", command=self.pause_attendance_session)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = ttk.Button(self.control_frame, text="Finalizar sesión", command=self.stop_attendance_session)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

    def start_attendance_session(self):
        self.attendance_manager.start_session()

    def pause_attendance_session(self):
        self.attendance_manager.pause_session()

    def stop_attendance_session(self):
        self.attendance_manager.stop_session()

    def update_student_status(self, student_id, status):
        self.attendance_manager.mark_attendance(student_id, status)
        self.load_student_list()

    def send_notification(self, phone_number, template, student_name):
        self.notification_manager.send_notification(phone_number, template, student_name)

    def view_notification_history(self):
        history = self.notification_manager.get_notification_history()
        for record in history:
            print(f"{record['timestamp']}: {record['phone_number']} - {record['message']}")

    def create_tooltips(self):
        self.tooltips = {
            self.start_button: "Start the attendance session",
            self.pause_button: "Pause the attendance session",
            self.stop_button: "Stop the attendance session"
        }
        for widget, text in self.tooltips.items():
            widget.bind("<Enter>", lambda e, t=text: self.show_tooltip(e, t))
            widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, text):
        x, y, _, _ = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(event.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()

    def create_context_menu(self):
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_student)
        self.context_menu.add_command(label="Delete", command=self.delete_student)
        self.student_list.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def edit_student(self):
        selected_item = self.student_list.selection()[0]
        student_id = self.student_list.item(selected_item, "values")[0]
        # Implement the edit functionality here

    def delete_student(self):
        selected_item = self.student_list.selection()[0]
        student_id = self.student_list.item(selected_item, "values")[0]
        # Implement the delete functionality here

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    database = Database("asisto_ya.db")
    security = Security()
    ui = UserInterface(root, database, security)
    root.mainloop()
