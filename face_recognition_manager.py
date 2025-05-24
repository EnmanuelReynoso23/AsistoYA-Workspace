import cv2
import os
import numpy as np
import time
import random
import string
import shutil
from datetime import datetime

class FaceRecognitionManager:
    def __init__(self, faces_dir="faces", confidence_threshold=80):
        self.faces_dir = faces_dir
        os.makedirs(self.faces_dir, exist_ok=True)
        
        # Load face detection models
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Create LBPH recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.confidence_threshold = confidence_threshold
        
        # Make backup directory for storing model data
        self.backup_dir = os.path.join(self.faces_dir, "backup")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.labels = {}
        self.codes_map = {}  # Mapping of names to student codes
        self.train_model()

    def train_model(self):
        """Train the face recognition model with saved face data"""
        faces = []
        labels = []
        label_map = {}
        name_to_label = {}
        code_map = {}
        label_id = 0
        
        print("Training face recognition model...")
        
        # Loop through all face images in the faces directory
        for filename in os.listdir(self.faces_dir):
            if filename.endswith(".npy"):
                try:
                    # Extract name and code (name can have underscores and code and timestamp go at the end)
                    name_code_time = filename[:-4]
                    # Split by last underscore (timestamp)
                    if "_" in name_code_time:
                        name_code, timestamp = name_code_time.rsplit("_", 1)
                    else:
                        name_code = name_code_time
                    # Split by second-to-last underscore (code)
                    if "_" in name_code:
                        name, code = name_code.rsplit("_", 1)
                    else:
                        name = name_code
                        code = ""
                    # Assign unique label per person (name)
                    if name not in name_to_label:
                        name_to_label[name] = label_id
                        label_map[label_id] = name
                        code_map[name] = code  # Save code associated with name
                        label_id += 1
                    img_data = np.load(os.path.join(self.faces_dir, filename))
                    faces.append(img_data)
                    labels.append(name_to_label[name])
                except Exception as e:
                    print(f"Error processing face file {filename}: {e}")
                    continue
                    
        if faces:
            print(f"Training model with {len(faces)} faces from {len(name_to_label)} unique individuals")
            # Train the recognizer and save labels and codes maps
            self.recognizer.train(faces, np.array(labels))
            self.labels = label_map
            self.codes_map = code_map
            # Save model for backup
            self.save_model()
        else:
            print("No faces found for training. Using empty model.")
            self.labels = {}
            self.codes_map = {}

    def save_model(self):
        """Save the trained model and mappings"""
        try:
            # Save time-stamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_file = os.path.join(self.backup_dir, f"model_{timestamp}.yml")
            self.recognizer.write(model_file)
            
            # Save latest model
            latest_model = os.path.join(self.faces_dir, "model.yml")
            self.recognizer.write(latest_model)
            
            # Save labels and codes maps
            import json
            with open(os.path.join(self.faces_dir, "labels.json"), "w") as f:
                json.dump(self.labels, f)
            with open(os.path.join(self.faces_dir, "codes.json"), "w") as f:
                json.dump(self.codes_map, f)
                
            print("Model and mappings saved successfully")
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self):
        """Load a previously saved model and mappings"""
        try:
            model_file = os.path.join(self.faces_dir, "model.yml")
            if os.path.exists(model_file):
                self.recognizer.read(model_file)
                
                # Load labels and codes maps
                import json
                with open(os.path.join(self.faces_dir, "labels.json"), "r") as f:
                    # Convert keys from strings to integers
                    self.labels = {int(k): v for k, v in json.load(f).items()}
                with open(os.path.join(self.faces_dir, "codes.json"), "r") as f:
                    self.codes_map = json.load(f)
                    
                print("Model and mappings loaded successfully")
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def save_face(self, face_img, name):
        """Save a face image for training"""
        # Generate unique code: initials + 4 random digits
        parts = name.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[1][0].upper()
        else:
            initials = name[:2].upper()
        code = initials + ''.join(random.choices(string.digits, k=4))
        # Add timestamp to allow multiple faces per person
        timestamp = int(time.time())
        
        # Save the face image
        filename = f"{name}_{code}_{timestamp}.npy"
        filepath = os.path.join(self.faces_dir, filename)
        np.save(filepath, face_img)
        
        print(f"Face saved as {filename}")
        
        # Retrain the model with the new face
        self.train_model()
        return code

    def recognize_face(self, face_img):
        """Recognize a face and return the name and confidence"""
        if not self.labels:
            return "Desconocido", 100.0
            
        try:
            # Try to predict the face
            label, confidence = self.recognizer.predict(face_img)
            name = self.labels.get(label, "Desconocido")
            return name, confidence
        except Exception as e:
            print(f"Error recognizing face: {e}")
            return "Desconocido", 100.0
        
    def get_student_code(self, name):
        """Get the student code associated with a recognized name"""
        return self.codes_map.get(name, "")
        
    def preprocess_face(self, face_img):
        """Preprocess face for better recognition"""
        try:
            # Resize to standard size
            face_img = cv2.resize(face_img, (200, 200))
            
            # Convert to grayscale if not already
            if len(face_img.shape) > 2:
                face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                
            # Apply histogram equalization to improve contrast
            face_img = cv2.equalizeHist(face_img)
            
            return face_img
        except Exception as e:
            print(f"Error preprocessing face: {e}")
            return face_img
            
    def detect_faces(self, frame):
        """Detect faces in a frame using cascade classifier"""
        if frame is None:
            return []
            
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return faces
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
            
    def capture_training_faces(self, camera, name, num_faces=5):
        """Capture multiple face samples for training"""
        if not camera.capture.isOpened():
            print("Error: Camera not available")
            return False
            
        faces_captured = 0
        codes = []
        
        print(f"Capturing {num_faces} training faces for {name}...")
        
        # We'll try up to 30 frames to get num_faces good samples
        for _ in range(30):
            if faces_captured >= num_faces:
                break
                
            ret, frame = camera.capture.read()
            if not ret:
                print("Error capturing frame")
                continue
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 1:  # We want just one face per frame
                (x, y, w, h) = faces[0]
                # Extract and preprocess the face
                face_img = gray[y:y+h, x:x+w]
                face_img_processed = self.preprocess_face(face_img)
                
                # Save the face
                code = self.save_face(face_img_processed, name)
                codes.append(code)
                faces_captured += 1
                
                # Display feedback
                print(f"Captured sample {faces_captured}/{num_faces}")
                
                # Wait a bit between captures to get different angles/expressions
                time.sleep(0.5)
                
        print(f"Finished capturing {faces_captured} face samples")
        return codes if codes else False
