# main.py
# Archivo principal de arranque para AsistoYA


if __name__ == "__main__":
    import ttkbootstrap as ttk
    from face_attendance_system import AdvancedAttendanceApp
    root = ttk.Window(themename="cosmo")
    app = AdvancedAttendanceApp(root)
    root.mainloop()
