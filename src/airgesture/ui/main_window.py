from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import logging
import sys
import os

from src.airgesture.ui.components import StatusLabel, ControlButton
from src.airgesture.core.gesture_detector import GestureDetector
from src.airgesture.utils.config import CAMERA_CONFIG

logger = logging.getLogger(__name__)

class AirGestureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Air Gesture Control")
        self.setGeometry(100, 100, 1400, 900)
        self.setFixedSize(1400, 900)
        
        # Initialize gesture detector
        try:
            self.gesture_detector = GestureDetector()
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}")
            error_msg = str(e)
            
            if "mediapipe" in error_msg.lower():
                error_msg = ("Failed to initialize MediaPipe hand tracking.\n\n"
                           "This could be due to:\n"
                           "1. Missing model files - ensure you have internet connection for first run\n"
                           "2. Insufficient permissions to download/access model files\n"
                           "3. Antivirus blocking access to temporary files\n\n"
                           "Try running the application with administrator privileges or temporarily "
                           "disable your antivirus software.")
            elif "camera" in error_msg.lower():
                error_msg = (f"{error_msg}\n\n"
                           "Please check if:\n"
                           "1. Your camera is properly connected\n"
                           "2. No other application is using the camera\n"
                           "3. You have granted camera permissions to the application\n"
                           "4. Your camera drivers are up to date")
                
            QMessageBox.critical(self, "Initialization Error", error_msg)
            self.gesture_detector = None
            sys.exit(1)
            
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
        
        # Add title
        self.add_title(main_layout)
        
        # Add status bar
        self.add_status_bar(main_layout)
        
        # Add camera display
        self.add_camera_display(main_layout)
        
        # Add control buttons
        self.add_control_buttons(main_layout)
        
        # Add info container
        self.add_info_container(main_layout)
        
    def add_title(self, layout):
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
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
    def add_status_bar(self, layout):
        self.status_label = StatusLabel("Status: Ready")
        self.status_label.setFixedHeight(70)
        layout.addWidget(self.status_label)
        
    def add_camera_display(self, layout):
        camera_container = QFrame()
        camera_container.setFixedHeight(400)
        camera_container.setStyleSheet("""
            QFrame {
                background: rgba(13, 71, 161, 0.6);
                border-radius: 25px;
                padding: 10px;
                border: 3px solid #2196f3;
                margin: 5px;
            }
        """)
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setContentsMargins(10, 10, 10, 10)
        
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
        layout.addWidget(camera_container)
        
    def add_control_buttons(self, layout):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setContentsMargins(20, 0, 20, 20)
        
        self.start_button = ControlButton("Start")
        self.start_button.setFixedWidth(260)
        self.start_button.clicked.connect(self.toggle_gesture_control)
        button_layout.addWidget(self.start_button)
        
        help_button = ControlButton("Help")
        help_button.setFixedWidth(260)
        help_button.clicked.connect(self.show_help)
        button_layout.addWidget(help_button)
        
        layout.addLayout(button_layout)
        
    def add_info_container(self, layout):
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
        
        # Add brightness and volume indicators
        self.brightness_value, self.volume_value = self.gesture_detector.add_indicators(info_layout)
        
        layout.addWidget(info_container)
        
    def update_frame(self):
        """Update the camera feed and process gestures."""
        try:
            if self.gesture_detector is None:
                return
                
            frame = self.gesture_detector.process_frame()
            if frame is not None:
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.camera_label.setPixmap(scaled_pixmap)
            else:
                self.status_label.setText("Status: Camera not available")
        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")
            print(f"Error in update_frame: {str(e)}")
        
    def toggle_gesture_control(self):
        """Toggle gesture control on/off."""
        self.gesture_detector.toggle()
        self.start_button.setText("Stop" if self.gesture_detector.is_running else "Start")
        self.update_button_style()
        
    def update_button_style(self):
        colors = {
            'normal': ('#f44336', '#d32f2f') if self.gesture_detector.is_running else ('#2196f3', '#1976d2'),
            'hover': ('#d32f2f', '#c62828') if self.gesture_detector.is_running else ('#1976d2', '#1565c0'),
            'pressed': ('#c62828', '#b71c1c') if self.gesture_detector.is_running else ('#1565c0', '#0d47a1')
        }
        self.start_button.update_colors(colors)
        
    def show_help(self):
        """Show help message with gesture controls."""
        self.gesture_detector.show_help(self)
        
    def closeEvent(self, event):
        """Handle application closure."""
        self.gesture_detector.cleanup()
        event.accept() 