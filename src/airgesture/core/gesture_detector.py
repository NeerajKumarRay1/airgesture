import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc
import time
import os
import sys
import tempfile
from pathlib import Path
from pynput.mouse import Controller, Button
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from src.airgesture.utils.config import (CAMERA_CONFIG, GESTURE_CONFIG, 
                                   GESTURE_THRESHOLDS, SYSTEM_CONFIG)

def get_mediapipe_model_path():
    """Get the correct path to MediaPipe model files whether running from source or executable."""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running from source
        base_path = os.path.dirname(mp.__file__)
    return os.path.join(base_path, 'mediapipe', 'modules')

class GestureDetector:
    def __init__(self):
        # Initialize camera
        self.cap = None
        self.init_camera()
        
        # Initialize MediaPipe
        try:
            # Set the model path for MediaPipe
            model_path = get_mediapipe_model_path()
            os.environ['MEDIAPIPE_MODEL_PATH'] = model_path
            
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=GESTURE_CONFIG['max_num_hands'],
                min_detection_confidence=GESTURE_CONFIG['min_detection_confidence'],
                min_tracking_confidence=GESTURE_CONFIG['min_tracking_confidence'],
                model_complexity=GESTURE_CONFIG['model_complexity']
            )
            self.mp_drawing = mp.solutions.drawing_utils
        except Exception as e:
            error_msg = str(e)
            if "Could not find the model file" in error_msg or "path does not exist" in error_msg:
                error_msg = ("Failed to initialize MediaPipe hand tracking.\n\n"
                           "This could be due to:\n"
                           "1. Missing model files\n"
                           "2. Insufficient permissions to access model files\n"
                           "3. Antivirus blocking access to files\n\n"
                           f"Model path: {model_path}\n"
                           "Try running the application with administrator privileges.")
            raise RuntimeError(error_msg)
        
        # Initialize controllers
        self.mouse = Controller()
        self.init_volume_control()
        
        # Initialize state
        self.is_running = False
        self.cursor_smoothing = GESTURE_CONFIG['cursor_smoothing']
        self.smoothed_cursor_x = None
        self.smoothed_cursor_y = None
        self.cursor_active = True
        self.click_ready = False
        self.last_palm_open_time = 0
        self.palm_open_cooldown = GESTURE_CONFIG['palm_open_cooldown']
        
    def init_camera(self):
        """Initialize the camera with proper error handling."""
        available_cameras = []
        
        # Try to find available cameras
        for i in range(4):  # Check first 4 camera indices
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow on Windows
                if cap.isOpened():
                    available_cameras.append(i)
                    cap.release()
                    print(f"Found camera at index {i}")
            except Exception as e:
                print(f"Error checking camera {i}: {str(e)}")
                
        if not available_cameras:
            raise RuntimeError("No cameras found. Please check if your camera is connected and not in use by another application.")
        
        # Try to open the first available camera
        for camera_index in available_cameras:
            try:
                self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                if self.cap.isOpened():
                    print(f"Successfully opened camera {camera_index}")
                    
                    # Set camera properties
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG['width'])
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG['height'])
                    self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['fps'])
                    
                    # Verify camera settings
                    actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
                    
                    print(f"Camera initialized with resolution: {actual_width}x{actual_height} at {actual_fps}fps")
                    break
            except Exception as e:
                print(f"Error opening camera {camera_index}: {str(e)}")
                continue
                
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError("Failed to open any camera. Please check if your camera is connected and not in use by another application.")
            
    def init_volume_control(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = interface.QueryInterface(IAudioEndpointVolume)
        except Exception as e:
            print(f"Could not initialize volume control: {e}")
            self.volume = None
            
    def add_indicators(self, layout):
        # Create brightness indicator
        brightness_container = QFrame()
        brightness_container.setFixedHeight(60)
        brightness_container.setStyleSheet("""
            QFrame {
                background: rgba(33, 150, 243, 0.2);
                border-radius: 10px;
                border: 1px solid #2196f3;
            }
        """)
        brightness_layout = QHBoxLayout(brightness_container)
        brightness_layout.setContentsMargins(20, 5, 20, 5)
        brightness_layout.setSpacing(15)

        brightness_label = QLabel("Brightness")
        brightness_label.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-size: 22px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        brightness_label.setFixedWidth(120)
        brightness_layout.addWidget(brightness_label)

        brightness_value = QLabel("--")
        brightness_value.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        brightness_value.setFixedWidth(70)
        brightness_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        brightness_layout.addWidget(brightness_value)
        brightness_layout.addStretch()

        layout.addWidget(brightness_container)

        # Create volume indicator
        volume_container = QFrame()
        volume_container.setFixedHeight(60)
        volume_container.setStyleSheet("""
            QFrame {
                background: rgba(33, 150, 243, 0.2);
                border-radius: 10px;
                border: 1px solid #2196f3;
            }
        """)
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(20, 5, 20, 5)
        volume_layout.setSpacing(15)

        volume_label = QLabel("Volume")
        volume_label.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-size: 22px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        volume_label.setFixedWidth(120)
        volume_layout.addWidget(volume_label)

        volume_value = QLabel("--")
        volume_value.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        volume_value.setFixedWidth(70)
        volume_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        volume_layout.addWidget(volume_value)
        volume_layout.addStretch()

        layout.addWidget(volume_container)
        
        return brightness_value, volume_value
        
    def process_frame(self):
        """Process a single frame and return it with annotations."""
        try:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame from camera")
                return None
                
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process gestures if running
            if self.is_running:
                try:
                    results = self.hands.process(frame_rgb)
                    current_time = time.time()
                    
                    if results.multi_hand_landmarks:
                        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                            results.multi_handedness):
                            # Draw landmarks
                            self.mp_drawing.draw_landmarks(frame_rgb, hand_landmarks, 
                                                         self.mp_hands.HAND_CONNECTIONS)
                            
                            if handedness.classification[0].label == "Right":
                                self.process_right_hand(hand_landmarks)
                            else:
                                self.process_left_hand(hand_landmarks, current_time)
                                
                        if len(results.multi_hand_landmarks) == 2:
                            self.check_namaste_gesture(results.multi_hand_landmarks[0],
                                                     results.multi_hand_landmarks[1])
                except Exception as e:
                    print(f"Error processing gestures: {str(e)}")
                    
            return frame_rgb
        except Exception as e:
            print(f"Error in process_frame: {str(e)}")
            return None
        
    def process_right_hand(self, hand_landmarks):
        """Process right hand gestures."""
        if self.is_fingers_apart(hand_landmarks):
            self.cursor_active = False
            self.click_ready = True
        else:
            self.cursor_active = True
            self.click_ready = False
            
        if self.cursor_active and self.is_two_fingers_up(hand_landmarks):
            self.update_cursor_position(hand_landmarks)
            
        if not self.cursor_active and self.click_ready:
            if self.is_pinch(hand_landmarks):
                self.mouse.click(Button.left, 1)
                self.click_ready = False
            elif self.is_middle_thumb_tap(hand_landmarks):
                self.mouse.click(Button.right, 1)
                self.click_ready = False
                
        if self.is_pinky_finger_up(hand_landmarks):
            self.adjust_brightness(1)
        elif self.is_pinky_finger_down(hand_landmarks):
            self.adjust_brightness(-1)
            
    def process_left_hand(self, hand_landmarks, current_time):
        """Process left hand gestures."""
        if self.is_index_middle_fingers_together(hand_landmarks):
            if self.is_two_fingers_up(hand_landmarks):
                self.mouse.scroll(0, SYSTEM_CONFIG['scroll_step'])
            elif self.is_five_fingers_down(hand_landmarks):
                self.mouse.scroll(0, -SYSTEM_CONFIG['scroll_step'])
                
        if self.is_full_palm_open(hand_landmarks):
            if current_time - self.last_palm_open_time > self.palm_open_cooldown:
                pyautogui.hotkey('win', 'tab')
                self.last_palm_open_time = current_time
                
        if self.is_index_finger_up(hand_landmarks):
            self.adjust_volume(1)
        else:
            self.adjust_volume(-1)
            
    def update_cursor_position(self, hand_landmarks):
        """Update cursor position based on hand landmarks."""
        screen_width, screen_height = pyautogui.size()
        cursor_x = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
        cursor_y = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)
        
        self.smoothed_cursor_x = self.apply_smoothing(cursor_x, self.smoothed_cursor_x)
        self.smoothed_cursor_y = self.apply_smoothing(cursor_y, self.smoothed_cursor_y)
        
        self.mouse.position = (int(self.smoothed_cursor_x), int(self.smoothed_cursor_y))
        
    def apply_smoothing(self, new_value, smoothed_value):
        """Apply exponential smoothing to a value."""
        if smoothed_value is None:
            return new_value
        return self.cursor_smoothing * new_value + (1 - self.cursor_smoothing) * smoothed_value
        
    def adjust_brightness(self, direction):
        """Adjust screen brightness."""
        try:
            current = sbc.get_brightness(display=0)[0]
            new_value = min(max(current + direction * SYSTEM_CONFIG['brightness_step'], 0), 100)
            sbc.set_brightness(new_value, display=0)
        except Exception as e:
            print(f"Could not adjust brightness: {e}")
            
    def adjust_volume(self, direction):
        """Adjust system volume."""
        try:
            if self.volume:
                current = self.volume.GetMasterVolumeLevelScalar()
                new_value = min(max(current + direction * SYSTEM_CONFIG['volume_step'], 0.0), 1.0)
                self.volume.SetMasterVolumeLevelScalar(new_value, None)
        except Exception as e:
            print(f"Could not adjust volume: {e}")
            
    def is_two_fingers_up(self, hand_landmarks):
        """Check if index and middle fingers are up."""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        return (index_tip < index_pip and middle_tip < middle_pip and 
                ring_tip > middle_tip and pinky_tip > middle_tip)
                
    def is_pinch(self, hand_landmarks):
        """Check if thumb and index finger are pinched."""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < GESTURE_THRESHOLDS['pinch_distance']
        
    def is_middle_thumb_tap(self, hand_landmarks):
        """Check if thumb and middle finger are tapped."""
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        distance = np.linalg.norm(np.array([middle_tip.x, middle_tip.y, middle_tip.z]) - 
                                np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < GESTURE_THRESHOLDS['pinch_distance']
        
    def is_fingers_apart(self, hand_landmarks):
        """Check if fingers are spread apart."""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
        return distance > GESTURE_THRESHOLDS['fingers_apart_distance']
        
    def is_five_fingers_up(self, hand_landmarks):
        """Check if all fingers are up."""
        return all(hand_landmarks.landmark[finger].y < hand_landmarks.landmark[finger - 2].y 
                  for finger in [self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
                               self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                               self.mp_hands.HandLandmark.RING_FINGER_TIP,
                               self.mp_hands.HandLandmark.PINKY_TIP])
                               
    def is_five_fingers_down(self, hand_landmarks):
        """Check if all fingers are down."""
        return all(hand_landmarks.landmark[finger].y > hand_landmarks.landmark[finger - 2].y 
                  for finger in [self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
                               self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                               self.mp_hands.HandLandmark.RING_FINGER_TIP,
                               self.mp_hands.HandLandmark.PINKY_TIP])
                               
    def is_pinky_finger_up(self, hand_landmarks):
        """Check if pinky finger is up."""
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        pinky_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y
        return pinky_tip < pinky_pip
        
    def is_pinky_finger_down(self, hand_landmarks):
        """Check if pinky finger is down while others are closed."""
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        pinky_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y
        
        return (pinky_tip > pinky_pip and 
                index_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                middle_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                ring_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and
                thumb_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP].y)
                
    def is_index_middle_fingers_together(self, hand_landmarks):
        """Check if index and middle fingers are close together."""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
        return distance < GESTURE_THRESHOLDS['fingers_together_distance']
        
    def is_full_palm_open(self, hand_landmarks):
        """Check if palm is fully open."""
        return self.is_five_fingers_up(hand_landmarks)
        
    def is_index_finger_up(self, hand_landmarks):
        """Check if index finger is up."""
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        return index_tip < index_pip
        
    def check_namaste_gesture(self, hand_landmarks1, hand_landmarks2):
        """Check if hands are in namaste position."""
        wrist1 = hand_landmarks1.landmark[self.mp_hands.HandLandmark.WRIST]
        wrist2 = hand_landmarks2.landmark[self.mp_hands.HandLandmark.WRIST]
        distance = np.linalg.norm(np.array([wrist1.x, wrist1.y]) - 
                                np.array([wrist2.x, wrist2.y]))
        return distance < GESTURE_THRESHOLDS['namaste_distance']
        
    def toggle(self):
        """Toggle gesture detection on/off."""
        self.is_running = not self.is_running
        
    def show_help(self, parent):
        """Show help message."""
        help_text = """
Air Gesture Control - Help Guide

Right Hand Controls:
• Two fingers up (with fingers together): Move cursor
• Spread fingers apart, then pinch: Left click
• Spread fingers apart, then middle-thumb tap: Right click
• Pinky finger up/down: Adjust screen brightness

Left Hand Controls:
• Index and middle fingers together up: Scroll up
• All fingers down: Scroll down
• Open palm: Task view (Win+Tab)
• Index finger up: Increase volume
• Other fingers: Decrease volume

Both Hands:
• Namaste gesture (both hands together): Exit application

Tips for Better Control:
• Keep your hand steady for better cursor control
• Click 'Stop' to pause gesture control
• Make sure your hands are well-lit and visible to the camera
• Practice gestures slowly at first for better accuracy
"""
        msg = QMessageBox(parent)
        msg.setWindowTitle("Help - Air Gesture Control")
        msg.setText(help_text)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 10px;
                background: rgba(33, 150, 243, 0.1);
                border-radius: 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1976d2, stop:1 #1565c0);
                border: 1px solid #64b5f6;
            }
        """)
        msg.exec_()
        
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
            if hasattr(self, 'hands') and self.hands is not None:
                self.hands.close()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}") 