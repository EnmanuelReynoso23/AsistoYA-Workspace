import cv2

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.capture = cv2.VideoCapture(self.source)
        self.configure_camera()

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
        # Placeholder for frame processing logic
        # This could include face detection/recognition using OpenCV or YOLOv8
        return frame

if __name__ == "__main__":
    camera = Camera()
    camera.start_capture()
