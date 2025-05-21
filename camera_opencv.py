import cv2
from attendance import AttendanceManager

def list_cameras(max_tested=5):
    """Devuelve una lista de índices de cámaras disponibles."""
    available = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available

def main():
    print("Cámaras disponibles:")
    cameras = list_cameras(10)
    for idx in cameras:
        print(f"  Cámara {idx}")
    if not cameras:
        print("No se detectaron cámaras.")
        return
    cam_idx = int(input(f"Selecciona el índice de cámara a usar [{cameras[0]}]: ") or cameras[0])
    cap = cv2.VideoCapture(cam_idx)
    attendance = AttendanceManager()
    print("Presiona 'a' para marcar asistencia, 'q' para salir.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar imagen.")
            break
        cv2.imshow('Cámara', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):
            student_id = input("ID del estudiante: ")
            attendance.mark_attendance(student_id, "presente")
            print(f"Asistencia marcada para {student_id}")
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    print("Asistencias registradas:")
    attendance.print_attendance_report('2000-01-01', '2100-01-01')

if __name__ == "__main__":
    main()
