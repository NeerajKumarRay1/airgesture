import sys
import cv2
import numpy as np
import pyautogui
import screen_brightness_control as sbc
import time
from pynput.mouse import Controller, Button
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import mediapipe as mp
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QMessageBox,
                            QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from config import (LOGGING_CONFIG, CAMERA_CONFIG, GESTURE_CONFIG, 
                   GESTURE_THRESHOLDS, SYSTEM_CONFIG)

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

class StatusLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #1a237e, stop:1 #0d47a1);
                color: #ffffff;
                padding: 12px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #2196f3;
                margin: 5px;
            }
            QLabel:hover {
                border: 2px solid #64b5f6;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #0d47a1, stop:1 #1a237e);
            }
        """)
        self.setAlignment(Qt.AlignCenter)

class ControlButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1976d2, stop:1 #1565c0);
                border: 2px solid #64b5f6;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1565c0, stop:1 #0d47a1);
                transform: translateY(1px);
            }
        """)

class AirGestureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Air Gesture Control")
        self.setGeometry(100, 100, 1400, 900)
        self.setFixedSize(1400, 900)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        self.is_running = False
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logger.error("Failed to open camera")
            QMessageBox.critical(self, "Error", "Failed to open camera")
            sys.exit(1)
            
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG['height'])
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['fps'])
            
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=GESTURE_CONFIG['max_num_hands'],
            min_detection_confidence=GESTURE_CONFIG['min_detection_confidence'],
            min_tracking_confidence=GESTURE_CONFIG['min_tracking_confidence'],
            model_complexity=GESTURE_CONFIG['model_complexity']
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize mouse controller
        self.mouse = Controller()
        
        # Initialize volume control
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = interface.QueryInterface(IAudioEndpointVolume)
        except Exception as e:
            logger.error(f"Could not initialize volume control: {e}")
            self.volume = None
            
        # Initialize state variables
        self.cursor_smoothing = GESTURE_CONFIG['cursor_smoothing']
        self.smoothed_cursor_x = None
        self.smoothed_cursor_y = None
        self.cursor_active = True
        self.click_ready = False
        self.last_palm_open_time = 0
        self.palm_open_cooldown = GESTURE_CONFIG['palm_open_cooldown']
        
        # Initialize UI
        self.init_ui()
        
        # Setup timer for camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 20, 30, 30)
        
        # Create title with modern styling
        title = QLabel("Air Gesture Control")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 42px;
                font-weight: bold;
                padding: 25px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #2196f3, stop:1 #1976d2);
                border-radius: 25px;
                border: 2px solid #64b5f6;
                margin: 20px;
            }
            QLabel:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1976d2, stop:1 #1565c0);
                border: 2px solid #90caf9;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create status bar with modern styling
        self.status_label = StatusLabel("Status: Ready")
        self.status_label.setFixedHeight(70)
        main_layout.addWidget(self.status_label)
        
        # Create camera display container with modern styling
        camera_container = QFrame()
        camera_container.setFixedHeight(400)
        camera_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #1a237e, stop:1 #0d47a1);
                border-radius: 25px;
                padding: 10px;
                border: 3px solid #2196f3;
                margin: 5px;
            }
            QFrame:hover {
                border: 3px solid #64b5f6;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #0d47a1, stop:1 #1a237e);
            }
        """)
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create camera display with modern styling
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(600, 350)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                border-radius: 20px;
                background: rgba(0, 0, 0, 0.2);
                border: 2px solid #2196f3;
            }
        """)
        camera_layout.addWidget(self.camera_label, 0, Qt.AlignCenter)
        
        main_layout.addWidget(camera_container)
        
        # Add spacing between camera and buttons
        main_layout.addSpacing(10)
        
        # Create control buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setContentsMargins(20, 0, 20, 20)
        
        # Start/Stop button
        self.start_button = ControlButton("Start")
        self.start_button.setFixedWidth(260)
        self.start_button.clicked.connect(self.toggle_gesture_control)
        button_layout.addWidget(self.start_button)
        
        # Help button
        help_button = ControlButton("Help")
        help_button.setFixedWidth(260)
        help_button.clicked.connect(self.show_help)
        button_layout.addWidget(help_button)
        
        main_layout.addLayout(button_layout)
        
        # Create status indicators container
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background: rgba(13, 71, 161, 0.6);
                border-radius: 15px;
                padding: 15px;
                border: 2px solid #2196f3;
                margin: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(15)
        info_layout.setContentsMargins(15, 15, 15, 15)

        # Create brightness indicator
        brightness_container = QFrame()
        brightness_container.setFixedHeight(50)
        brightness_container.setStyleSheet("""
            QFrame {
                background: rgba(33, 150, 243, 0.2);
                border-radius: 10px;
                border: 1px solid #2196f3;
            }
        """)
        brightness_layout = QHBoxLayout(brightness_container)
        brightness_layout.setContentsMargins(15, 0, 15, 0)
        brightness_layout.setSpacing(10)

        brightness_label = QLabel("Brightness:")
        brightness_label.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-size: 20px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        brightness_label.setFixedWidth(100)
        brightness_layout.addWidget(brightness_label)

        self.brightness_value = QLabel("--")
        self.brightness_value.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.brightness_value.setFixedWidth(60)
        self.brightness_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        brightness_layout.addWidget(self.brightness_value)
        brightness_layout.addStretch()

        info_layout.addWidget(brightness_container)

        # Create volume indicator
        volume_container = QFrame()
        volume_container.setFixedHeight(50)
        volume_container.setStyleSheet("""
            QFrame {
                background: rgba(33, 150, 243, 0.2);
                border-radius: 10px;
                border: 1px solid #2196f3;
            }
        """)
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(15, 0, 15, 0)
        volume_layout.setSpacing(10)

        volume_label = QLabel("Volume:")
        volume_label.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-size: 20px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        volume_label.setFixedWidth(100)
        volume_layout.addWidget(volume_label)

        self.volume_value = QLabel("--")
        self.volume_value.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-family: Arial;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.volume_value.setFixedWidth(60)
        self.volume_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        volume_layout.addWidget(self.volume_value)
        volume_layout.addStretch()

        info_layout.addWidget(volume_container)
        main_layout.addWidget(info_container)

        # Initialize values
        try:
            current_brightness = sbc.get_brightness(display=0)[0]
            self.brightness_value.setText(f"{int(current_brightness)}%")
        except Exception as e:
            logger.error(f"Could not get brightness: {e}")
            self.brightness_value.setText("N/A")

        try:
            if self.volume:
                current_volume = int(self.volume.GetMasterVolumeLevelScalar() * 100)
                self.volume_value.setText(f"{current_volume}%")
            else:
                self.volume_value.setText("N/A")
        except Exception as e:
            logger.error(f"Could not get volume: {e}")
            self.volume_value.setText("N/A")
        
    def apply_exponential_smoothing(self, new_value, smoothed_value, smoothing_factor):
        if smoothed_value is None:
            return new_value
        return smoothing_factor * new_value + (1 - smoothing_factor) * smoothed_value
        
    def is_two_fingers_up(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        return index_tip < index_pip and middle_tip < middle_pip and ring_tip > middle_tip and pinky_tip > middle_tip
        
    def is_pinch(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < GESTURE_THRESHOLDS['pinch_distance']
        
    def is_middle_thumb_tap(self, hand_landmarks):
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        distance = np.linalg.norm(np.array([middle_tip.x, middle_tip.y, middle_tip.z]) - np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < GESTURE_THRESHOLDS['pinch_distance']
        
    def is_fingers_apart(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
        return distance > GESTURE_THRESHOLDS['fingers_apart_distance']
        
    def is_five_fingers_up(self, hand_landmarks):
        return all(hand_landmarks.landmark[finger].y < hand_landmarks.landmark[finger - 2].y for finger in 
                   [self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                    self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.PINKY_TIP])
                    
    def is_five_fingers_down(self, hand_landmarks):
        return all(hand_landmarks.landmark[finger].y > hand_landmarks.landmark[finger - 2].y for finger in 
                   [self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                    self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.PINKY_TIP])
                    
    def is_pinky_finger_up(self, hand_landmarks):
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        pinky_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y
        return pinky_tip < pinky_pip
        
    def is_pinky_finger_down(self, hand_landmarks):
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        pinky_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y
        return pinky_tip > pinky_pip and index_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and \
               middle_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and \
               ring_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and \
               thumb_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP].y
               
    def is_index_middle_fingers_together(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
        return distance < 0.05
        
    def is_full_palm_open(self, hand_landmarks):
        return self.is_five_fingers_up(hand_landmarks)
        
    def is_index_finger_up(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        return index_tip < index_pip
        
    def is_namaste_gesture(self, hand_landmarks1, hand_landmarks2):
        wrist1 = hand_landmarks1.landmark[self.mp_hands.HandLandmark.WRIST]
        wrist2 = hand_landmarks2.landmark[self.mp_hands.HandLandmark.WRIST]
        distance = np.linalg.norm(np.array([wrist1.x, wrist1.y]) - np.array([wrist2.x, wrist2.y]))
        return distance < GESTURE_THRESHOLDS['namaste_distance']
        
    def update_frame(self):
        """Update the camera feed and process gestures."""
        try:
            ret, frame = self.cap.read()
            if not ret:
                return
                
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB for correct color display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process gestures if running
            if self.is_running:
                results = self.hands.process(frame_rgb)
                current_time = time.time()
                
                if results.multi_hand_landmarks:
                    hand_landmarks_list = list(zip(results.multi_hand_landmarks, results.multi_handedness))
                    
                    for hand_landmarks, handedness in hand_landmarks_list:
                        # Draw landmarks
                        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        
                        if handedness.classification[0].label == "Right":
                            if self.is_fingers_apart(hand_landmarks):
                                self.cursor_active = False
                                self.click_ready = True
                            else:
                                self.cursor_active = True
                                self.click_ready = False
                                
                            if self.cursor_active and self.is_two_fingers_up(hand_landmarks):
                                screen_width, screen_height = pyautogui.size()
                                cursor_x = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
                                cursor_y = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)
                                self.smoothed_cursor_x = self.apply_exponential_smoothing(cursor_x, self.smoothed_cursor_x, self.cursor_smoothing)
                                self.smoothed_cursor_y = self.apply_exponential_smoothing(cursor_y, self.smoothed_cursor_y, self.cursor_smoothing)
                                self.mouse.position = (int(self.smoothed_cursor_x), int(self.smoothed_cursor_y))
                                
                            if not self.cursor_active and self.click_ready and self.is_pinch(hand_landmarks):
                                self.mouse.click(Button.left, 1)
                                self.click_ready = False
                                
                            if not self.cursor_active and self.click_ready and self.is_middle_thumb_tap(hand_landmarks):
                                self.mouse.click(Button.right, 1)
                                self.click_ready = False
                                
                            if self.is_pinky_finger_up(hand_landmarks):
                                sbc.set_brightness(min(sbc.get_brightness(display=0)[0] + SYSTEM_CONFIG['brightness_step'], 100), display=0)
                            elif self.is_pinky_finger_down(hand_landmarks):
                                sbc.set_brightness(max(sbc.get_brightness(display=0)[0] - SYSTEM_CONFIG['brightness_step'], 0), display=0)
                                
                        elif handedness.classification[0].label == "Left":
                            if self.is_index_middle_fingers_together(hand_landmarks):
                                if self.is_two_fingers_up(hand_landmarks):
                                    self.mouse.scroll(0, SYSTEM_CONFIG['scroll_step'])  # Scroll up
                                elif self.is_five_fingers_down(hand_landmarks):
                                    self.mouse.scroll(0, -SYSTEM_CONFIG['scroll_step'])  # Scroll down
                                    
                            if self.is_full_palm_open(hand_landmarks) and (current_time - self.last_palm_open_time > self.palm_open_cooldown):
                                pyautogui.hotkey('win', 'tab')
                                self.last_palm_open_time = current_time
                                
                            if self.is_index_finger_up(hand_landmarks):
                                if self.volume:
                                    self.volume.SetMasterVolumeLevelScalar(min(self.volume.GetMasterVolumeLevelScalar() + SYSTEM_CONFIG['volume_step'], 1.0), None)
                            else:
                                if self.volume:
                                    self.volume.SetMasterVolumeLevelScalar(max(self.volume.GetMasterVolumeLevelScalar() - SYSTEM_CONFIG['volume_step'], 0.0), None)
                                    
                    if len(hand_landmarks_list) == 2:
                        hand_landmarks1, handedness1 = hand_landmarks_list[0]
                        hand_landmarks2, handedness2 = hand_landmarks_list[1]
                        if handedness1.classification[0].label != handedness2.classification[0].label:
                            if self.is_namaste_gesture(hand_landmarks1, hand_landmarks2):
                                self.close()
                                
                # Update status label
                if results.multi_hand_landmarks:
                    self.status_label.setText(f"Status: Active - {len(results.multi_hand_landmarks)} hand(s) detected")
                else:
                    self.status_label.setText("Status: Waiting for hands...")
            
            # Update brightness and volume values
            try:
                current_brightness = sbc.get_brightness(display=0)[0]
                self.brightness_value.setText(f"{int(current_brightness)}%")
            except Exception as e:
                logger.error(f"Could not update brightness: {e}")
                self.brightness_value.setText("N/A")
                
            try:
                if self.volume:
                    current_volume = int(self.volume.GetMasterVolumeLevelScalar() * 100)
                    self.volume_value.setText(f"{current_volume}%")
                else:
                    self.volume_value.setText("N/A")
            except Exception as e:
                logger.error(f"Could not update volume: {e}")
                self.volume_value.setText("N/A")
            
            # Convert frame to QImage and display
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logger.error(f"Error updating frame: {str(e)}")
            
    def toggle_gesture_control(self):
        """Toggle gesture control on/off."""
        self.is_running = not self.is_running
        self.start_button.setText("Stop" if self.is_running else "Start")
        
        # Define colors based on state
        if self.is_running:
            colors = {
                'normal': ('#f44336', '#d32f2f'),
                'hover': ('#d32f2f', '#c62828'),
                'pressed': ('#c62828', '#b71c1c')
            }
        else:
            colors = {
                'normal': ('#2196f3', '#1976d2'),
                'hover': ('#1976d2', '#1565c0'),
                'pressed': ('#1565c0', '#0d47a1')
            }
            
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {colors['normal'][0]}, stop:1 {colors['normal'][1]});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {colors['hover'][0]}, stop:1 {colors['hover'][1]});
                border: 2px solid #64b5f6;
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {colors['pressed'][0]}, stop:1 {colors['pressed'][1]});
                transform: translateY(1px);
            }}
        """)
        self.logger.info(f"{'Started' if self.is_running else 'Stopped'} gesture control")
            
    def show_help(self):
        """Show help message with gesture controls."""
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
        msg = QMessageBox(self)
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
        
    def closeEvent(self, event):
        """Handle application closure."""
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AirGestureApp()
    window.show()
    sys.exit(app.exec_())
