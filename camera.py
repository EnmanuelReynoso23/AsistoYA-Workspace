import cv2
import numpy as np
import os
import time
import threading

# Flag para indicar si se puede usar YOLO
USE_YOLO = False
try:
    from ultralytics import YOLO
    USE_YOLO = True
    print("[INFO] Ultralytics YOLO importado correctamente")
except ImportError:
    print("[INFO] No se pudo importar Ultralytics YOLO, se usará el detector de rostros de OpenCV")
except Exception as e:
    print(f"[ERROR] Error al importar Ultralytics YOLO: {e}")

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.capture = None
        self.is_running = False
        self.last_frame = None
        self.connect_camera()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # Try to load the YOLOv8 model for face detection if available
        self.model = None
        self.model_loaded = False
        if USE_YOLO:
            self.load_model_thread = threading.Thread(target=self.load_model)
            self.load_model_thread.daemon = True
            self.load_model_thread.start()
        else:
            print("[INFO] Usando detector de rostros Haar Cascade de OpenCV")

    def load_model(self):
        """Load YOLOv8 model in a separate thread to avoid blocking the UI"""
        try:
            if os.path.exists('yolov8n-face.pt') and USE_YOLO:
                print("[INFO] Cargando modelo de detección facial YOLOv8...")
                try:
                    self.model = YOLO('yolov8n-face.pt')
                    self.model_loaded = True
                    print("[INFO] ¡Modelo YOLOv8 cargado correctamente!")
                except Exception as e:
                    print(f"[ERROR] Error al cargar el modelo YOLOv8: {e}")
                    print("[INFO] Usando Haar Cascade como alternativa")
            else:
                if not os.path.exists('yolov8n-face.pt'):
                    print("[INFO] Modelo facial YOLOv8 no encontrado, usando Haar Cascade")
        except Exception as e:
            print(f"[ERROR] Error cargando modelo YOLOv8: {e}")
            print("[INFO] Usando detector Haar Cascade")

    def connect_camera(self):
        """Connect to the camera source with error handling"""
        try:
            if isinstance(self.source, str) and self.source.startswith("http"):
                # It's an IP camera URL
                print(f"Connecting to IP camera at {self.source}")
            else:
                # It's a local camera index
                print(f"Connecting to camera at index {self.source}")
            
            self.capture = cv2.VideoCapture(self.source)
            
            if not self.capture.isOpened():
                print(f"Failed to open camera at {self.source}")
                return False
                
            self.configure_camera()
            return True
        except Exception as e:
            print(f"Error connecting to camera: {e}")
            return False

    def configure_camera(self):
        """Configure camera properties for optimal face detection and image quality"""
        try:
            # Set higher resolution for better image quality
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Set FPS for smoother video
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            # Optimize image quality settings
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, 140)  # Slightly brighter
            self.capture.set(cv2.CAP_PROP_CONTRAST, 130)    # Better contrast
            self.capture.set(cv2.CAP_PROP_SATURATION, 120)  # Improved color saturation
            self.capture.set(cv2.CAP_PROP_SHARPNESS, 130)   # Sharper image
            
            # Enable auto exposure and focus for better image quality
            self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
            self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            # Get actual resolution to verify settings
            actual_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.capture.get(cv2.CAP_PROP_FPS)
            
            print(f"Camera configured: {actual_width}x{actual_height} @ {actual_fps}fps")
        except Exception as e:
            print(f"Error configuring camera: {e}")

    def change_camera(self, new_source):
        """Change the camera source"""
        self.stop_capture()
        time.sleep(0.5)  # Wait to ensure previous capture is released
        self.source = new_source
        success = self.connect_camera()
        return success

    def get_frame(self):
        """Get a frame from the camera with error handling"""
        if not self.capture or not self.capture.isOpened():
            return None
            
        try:
            ret, frame = self.capture.read()
            if not ret or frame is None:
                print("Failed to capture frame, attempting to reconnect...")
                self.reconnect()
                return None
            self.last_frame = frame
            return frame
        except Exception as e:
            print(f"Error capturing frame: {e}")
            self.reconnect()
            return None
            
    def reconnect(self):
        """Attempt to reconnect to the camera after failure"""
        print("Attempting to reconnect to camera...")
        if self.capture:
            self.capture.release()
        time.sleep(1)  # Wait before reconnecting

        self.connect_camera()

    def detect_faces(self, frame):
        """Detect faces in the frame using YOLOv8 or Haar cascade as fallback"""
        if frame is None:
            return []

        faces = []
        try:
            # Try YOLOv8 if model is loaded and enabled
            if USE_YOLO and self.model_loaded and self.model:
                try:
                    results = self.model(frame)
                    if hasattr(results[0].boxes, 'xyxy'):
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box[:4])
                            faces.append((x1, y1, x2-x1, y2-y1))
                except Exception as e:
                    print(f"[ERROR] Error en detección con YOLOv8: {e}")

            # If no faces detected with YOLOv8 or model not loaded, try Haar Cascade
            if not faces:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                haar_faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                faces = [(x, y, w, h) for (x, y, w, h) in haar_faces]

            return faces

        except Exception as e:
            print(f"Error detecting faces: {e}")
            # Fallback to Haar Cascade
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                haar_faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                return [(x, y, w, h) for (x, y, w, h) in haar_faces]
            except Exception as e2:
                print(f"Fallback face detection also failed: {e2}")
                return []

    def start_capture(self):
        """Start capturing frames in a loop"""
        self.is_running = True
        while self.is_running:
            frame = self.get_frame()
            if frame is not None:
                # Process the frame
                processed_frame = self.process_frame(frame)
                cv2.imshow('Camera', processed_frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.stop_capture()
        
    def process_frame(self, frame):
        """Process the camera frame for display"""
        # Create a copy to avoid modifying the original
        display_frame = frame.copy()
        
        # Detect faces
        faces = self.detect_faces(frame)
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        return display_frame
        
    def stop_capture(self):
        """Stop the camera capture"""
        self.is_running = False
        if self.capture:
            self.capture.release()
        cv2.destroyAllWindows()

    def is_camera_working(self):
        """Check if the camera is working properly"""
        if not self.capture or not self.capture.isOpened():
            return False
        ret, frame = self.capture.read()
        return ret and frame is not None

    def get_camera_list(max_cameras=5):
        """Get a list of available cameras"""
        available_cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

if __name__ == "__main__":
    camera = Camera()
    camera.start_capture()
