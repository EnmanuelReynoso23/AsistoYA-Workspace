import cv2
import numpy as np
import torch

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.capture = cv2.VideoCapture(self.source)
        self.configure_camera()
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

    def configure_camera(self):
        # Adjust lighting and contrast settings
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
        self.capture.set(cv2.CAP_PROP_CONTRAST, 0.5)

    def start_capture(self):
        while True:
            ret, frame = self.capture.read()
            if not ret:
                break

            # Process the frame (e.g., using OpenCV or YOLOv8)
            processed_frame = self.process_frame(frame)

            # Display the frame
            cv2.imshow('Camera', processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.capture.release()
        cv2.destroyAllWindows()

    def process_frame(self, frame):
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform face detection/recognition using YOLOv5
        results = self.model(rgb_frame)

        # Draw bounding boxes on the frame
        for result in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = result
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        return frame

if __name__ == "__main__":
    camera = Camera()
    camera.start_capture()
