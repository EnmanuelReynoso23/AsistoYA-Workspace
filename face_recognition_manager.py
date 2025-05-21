import cv2
import os
import numpy as np

class FaceRecognitionManager:
    def __init__(self, faces_dir="faces"):
        self.faces_dir = faces_dir
        os.makedirs(self.faces_dir, exist_ok=True)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.labels = {}
        self.train_model()

    def train_model(self):
        faces = []
        labels = []
        label_map = {}
        label_id = 0
        for filename in os.listdir(self.faces_dir):
            if filename.endswith(".npy"):
                name = filename[:-4]
                img_data = np.load(os.path.join(self.faces_dir, filename))
                faces.append(img_data)
                labels.append(label_id)
                label_map[label_id] = name
                label_id += 1
        if faces:
            self.recognizer.train(faces, np.array(labels))
            self.labels = label_map
        else:
            self.labels = {}

    def save_face(self, face_img, name):
        # Generar código único: iniciales + 4 dígitos aleatorios
        import random
        import string
        parts = name.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[1][0].upper()
        else:
            initials = name[:2].upper()
        code = initials + ''.join(random.choices(string.digits, k=4))
        filename = f"{name}_{code}.npy"
        np.save(os.path.join(self.faces_dir, filename), face_img)
        self.train_model()
        return code

    def recognize_face(self, face_img):
        if not self.labels:
            return None, 0.0
        label, confidence = self.recognizer.predict(face_img)
        name = self.labels.get(label, "Desconocido")
        return name, confidence
