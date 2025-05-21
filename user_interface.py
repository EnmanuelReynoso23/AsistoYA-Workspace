import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from camera import Camera
from attendance import AttendanceManager
from notifications import NotificationManager
from database import Database
from security import Security
from tkinter import Menu
from tkinter import messagebox
# from tkinter import ttk as tk

class UserInterface:
    def __init__(self, root, database, security):
        self.root = root
        self.database = database
        self.security = security
        self.camera_index = 0
        self.camera = Camera(self.camera_index)
        self.attendance_manager = AttendanceManager(database)
        self.notification_manager = NotificationManager(api_url="https://api.whatsapp.com/send", api_key="YOUR_API_KEY")
        self.tooltip = None
        self.available_cameras = self.list_cameras()
    def list_cameras(self, max_tested=5):
        import cv2
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"Cam {i}")
                cap.release()
        # Permitir agregar cámara IP manualmente
        available.append("Cámara IP...")
        return available
        
    def load_main_interface(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.create_main_interface()
        self.create_tooltips()
        self.create_context_menu()

    def create_main_interface(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Selector de cámara
        camera_select_frame = ttk.Frame(self.main_frame)
        camera_select_frame.pack(fill=tk.X, pady=5)
        ttk.Label(camera_select_frame, text="Seleccionar cámara:").pack(side=tk.LEFT, padx=5)
        self.camera_var = tk.StringVar(value=self.available_cameras[0])
        self.camera_menu = ttk.Combobox(camera_select_frame, values=self.available_cameras, textvariable=self.camera_var, width=15)
        self.camera_menu.pack(side=tk.LEFT)
        self.camera_menu.bind("<<ComboboxSelected>>", self.change_camera)

        self.create_camera_view()
        self.create_student_list()
        self.create_control_buttons()

    def change_camera(self, event=None):
        import cv2
        selected = self.camera_var.get()
        if selected == "Cámara IP...":
            import tkinter.simpledialog as simpledialog
            url = simpledialog.askstring("Cámara IP", "Introduce la URL del stream de la cámara IP (por ejemplo, rtsp o http):")
            if url:
                self.camera.capture.release()
                self.camera.capture = cv2.VideoCapture(url)
                self.camera_index = url
        else:
            idx = int(selected.replace("Cam ", ""))
            self.camera_index = idx
            self.camera.capture.release()
            self.camera.capture = cv2.VideoCapture(self.camera_index)

    def create_camera_view(self):
        self.camera_frame = ttk.Frame(self.main_frame)
        self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)

        # Botón para guardar rostro
        self.save_face_button = ttk.Button(self.camera_frame, text="Guardar rostro con nombre", command=self.save_face_from_gui)
        self.save_face_button.pack(pady=5)

        self.update_camera_view()

    def save_face_from_gui(self):
        import cv2
        from face_recognition_manager import FaceRecognitionManager
        gray = None
        frame = None
        ret, frame = self.camera.capture.read()
        if not ret:
            return
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_manager = FaceRecognitionManager()
        faces = face_manager.face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_img = gray[y:y+h, x:x+w]
            face_img_resized = cv2.resize(face_img, (200, 200))
            import tkinter.simpledialog as simpledialog
            nombre = simpledialog.askstring("Guardar rostro", "Nombre y apellido para guardar:")
            if nombre:
                code = face_manager.save_face(face_img_resized, nombre)
                tk.messagebox.showinfo("Éxito", f"Rostro guardado como {nombre}\nCódigo generado: {code}")
        else:
            tk.messagebox.showwarning("Advertencia", "No se detectó rostro para guardar.")

    def update_camera_view(self):
        try:
            import cv2
            from face_recognition_manager import FaceRecognitionManager
            ret, frame = self.camera.capture.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_manager = FaceRecognitionManager()
                faces = face_manager.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    face_img = gray[y:y+h, x:x+w]
                    face_img_resized = cv2.resize(face_img, (200, 200))
                    name, conf = face_manager.recognize_face(face_img_resized)
                    if name != "Desconocido" and conf < 80:
                        cv2.putText(frame, f"{name} ({conf:.0f})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                        self.attendance_manager.mark_attendance(name, "presente")
                    else:
                        cv2.putText(frame, "Desconocido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)
                # Mostrar frame en tkinter
                from PIL import Image, ImageTk
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                tk_img = ImageTk.PhotoImage(image=pil_img)
                self.camera_label.imgtk = tk_img
                self.camera_label.configure(image=tk_img)
        except Exception as e:
            print(f"Error updating camera view: {e}")
        self.root.after(10, self.update_camera_view)

    def create_student_list(self):
        self.student_list_frame = ttk.Frame(self.main_frame)
        self.student_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.student_list = ttk.Treeview(self.student_list_frame, columns=("ID", "Name", "Status", "Code"), show="headings")
        self.student_list.heading("ID", text="ID")
        self.student_list.heading("Name", text="Name")
        self.student_list.heading("Status", text="Status")
        self.student_list.heading("Code", text="Código")
        self.student_list.pack(fill=tk.BOTH, expand=True)

        self.load_student_list()

    def load_student_list(self):
        # Limpiar la lista actual
        for item in self.student_list.get_children():
            self.student_list.delete(item)
        # Cargar datos de la base de datos o usar datos de ejemplo
        if self.database:
            students = self.database.get_all_students()
            # Si tu base de datos soporta código, agrégalo aquí
            for student in students:
                code = student.get("code", "")
                self.student_list.insert("", "end", values=(student["id"], student["name"], student["status"], code))
        else:
            # Leer de los registros de asistencia en memoria para mostrar los estudiantes y sus códigos
            seen = set()
            students = []
            for record in self.attendance_manager.attendance_records:
                sid = record["Student ID"]
                if sid not in seen:
                    students.append({
                        "id": sid,
                        "name": sid,
                        "status": record["Status"],
                        "code": record.get("Code", "")
                    })
                    seen.add(sid)
            for student in students:
                self.student_list.insert("", "end", values=(student["id"], student["name"], student["status"], student["code"]))

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
