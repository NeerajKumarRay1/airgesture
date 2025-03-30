import cv2

class CameraManager:
    def __init__(self, width, height, fps):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera")
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 1)  # Flip horizontally

    def release(self):
        self.cap.release() 