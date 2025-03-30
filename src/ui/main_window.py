import cv2
import numpy as np
import pyautogui
import screen_brightness_control as sbc
import time
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QMessageBox, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from pynput.mouse import Controller, Button
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import mediapipe as mp

from src.ui.components.status_label import StatusLabel
from src.ui.components.control_button import ControlButton
from src.utils.camera import CameraManager
from src.gestures.detector import GestureDetector
from src.config.settings import CAMERA_CONFIG, GESTURE_CONFIG, SYSTEM_CONFIG
from src.config.logging_config import LOGGING_CONFIG

class AirGestureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_app()
        
    def init_app(self):
        """Initialize the application"""
        self.setup_window()
        self.setup_logging()
        self.init_components()
        self.init_ui()
        self.setup_timer()
        
    # ... rest of the AirGestureApp implementation 