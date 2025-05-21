import cv2
from face_recognition_manager import FaceRecognitionManager
from attendance import AttendanceManager

face_manager = FaceRecognitionManager()
attendance = AttendanceManager()

cap = cv2.VideoCapture(0)
print("Presiona 'g' para guardar rostro con nombre, 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_manager.face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w]
        face_img_resized = cv2.resize(face_img, (200, 200))
        name, conf = face_manager.recognize_face(face_img_resized)
        if name != "Desconocido" and conf < 80:
            cv2.putText(frame, f"{name} ({conf:.0f})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            attendance.mark_attendance(name, "presente")
        else:
            cv2.putText(frame, "Desconocido", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)
    cv2.imshow('Reconocimiento Facial', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('g'):
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_img = gray[y:y+h, x:x+w]
            face_img_resized = cv2.resize(face_img, (200, 200))
            nombre = input("Nombre para guardar: ")
            face_manager.save_face(face_img_resized, nombre)
            print(f"Rostro guardado como {nombre}")
        else:
            print("No se detectó rostro para guardar.")
    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
print("Asistencias registradas:")
attendance.print_attendance_report('2000-01-01', '2100-01-01')
