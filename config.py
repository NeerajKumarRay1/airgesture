import json
import os
import logging

# Logging
LOG_FILE = "air_gesture.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# Logging configuration dictionary
LOGGING_CONFIG = {
    'filename': LOG_FILE,
    'format': LOG_FORMAT,
    'level': LOG_LEVEL
}

# UI Settings
WINDOW_TITLE = "Air Gesture Control"
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
BACKGROUND_COLOR = "#1a1a1a"
BUTTON_COLOR = "#4a90e2"
BUTTON_HOVER_COLOR = "#357abd"
BUTTON_PRESSED_COLOR = "#2d6da3"
FONT_SIZE = 16

# Gesture Profiles
GESTURE_PROFILES_FILE = "gesture_profiles.json"

DEFAULT_PROFILE = {
    "name": "Default",
    "actions": {
        "volume_up": "Two fingers up - Right hand",
        "volume_down": "Two fingers down - Right hand",
        "brightness_up": "Two fingers up - Left hand",
        "brightness_down": "Two fingers down - Left hand",
        "mouse_move": "Index finger - Right hand",
        "left_click": "Pinch - Right hand",
        "right_click": "Pinch - Left hand",
        "scroll_up": "Palm up - Left hand",
        "scroll_down": "Palm down - Left hand"
    }
}

def load_gesture_profiles():
    if not os.path.exists(GESTURE_PROFILES_FILE):
        with open(GESTURE_PROFILES_FILE, 'w') as f:
            json.dump({"profiles": [DEFAULT_PROFILE]}, f, indent=4)
    
    with open(GESTURE_PROFILES_FILE, 'r') as f:
        return json.load(f)["profiles"]

def save_gesture_profiles(profiles):
    with open(GESTURE_PROFILES_FILE, 'w') as f:
        json.dump({"profiles": profiles}, f, indent=4)

# Camera Settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# MediaPipe Settings
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# Gesture Detection Settings
CURSOR_SMOOTHING = 0.3
PINCH_THRESHOLD = 0.12
FINGER_DISTANCE_THRESHOLD = 0.15
PALM_OPEN_COOLDOWN = 1

# Gesture Profiles
GESTURE_PROFILES = {
    "Default": {
        "pinch_threshold": 0.12,
        "finger_distance_threshold": 0.15,
        "cursor_smoothing": 0.3,
        "actions": {
            "volume_up": "Two fingers up - Right hand",
            "volume_down": "Two fingers down - Right hand",
            "brightness_up": "Two fingers up - Left hand",
            "brightness_down": "Two fingers down - Left hand",
            "mouse_move": "Index finger - Right hand",
            "left_click": "Pinch - Right hand",
            "right_click": "Middle thumb tap - Right hand",
            "scroll_up": "Two fingers up - Left hand",
            "scroll_down": "Five fingers down - Left hand",
            "task_view": "Five fingers up - Left hand"
        }
    },
    "Precise": {
        "pinch_threshold": 0.1,
        "finger_distance_threshold": 0.12,
        "cursor_smoothing": 0.4,
        "actions": {
            "volume_up": "Two fingers up - Right hand",
            "volume_down": "Two fingers down - Right hand",
            "brightness_up": "Two fingers up - Left hand",
            "brightness_down": "Two fingers down - Left hand",
            "mouse_move": "Index finger - Right hand",
            "left_click": "Pinch - Right hand",
            "right_click": "Middle thumb tap - Right hand",
            "scroll_up": "Two fingers up - Left hand",
            "scroll_down": "Five fingers down - Left hand",
            "task_view": "Five fingers up - Left hand"
        }
    },
    "Responsive": {
        "pinch_threshold": 0.15,
        "finger_distance_threshold": 0.18,
        "cursor_smoothing": 0.2,
        "actions": {
            "volume_up": "Two fingers up - Right hand",
            "volume_down": "Two fingers down - Right hand",
            "brightness_up": "Two fingers up - Left hand",
            "brightness_down": "Two fingers down - Left hand",
            "mouse_move": "Index finger - Right hand",
            "left_click": "Pinch - Right hand",
            "right_click": "Middle thumb tap - Right hand",
            "scroll_up": "Two fingers up - Left hand",
            "scroll_down": "Five fingers down - Left hand",
            "task_view": "Five fingers up - Left hand"
        }
    }
}

# Load gesture profiles
GESTURE_PROFILES = {profile["name"]: profile for profile in load_gesture_profiles()}

# Camera configuration
CAMERA_CONFIG = {
    'width': 640,
    'height': 360,
    'fps': 30
}

# Gesture detection settings
GESTURE_CONFIG = {
    'cursor_smoothing': 0.8,
    'palm_open_cooldown': 2.0,
    'min_detection_confidence': 0.8,
    'min_tracking_confidence': 0.8,
    'max_num_hands': 2,
    'model_complexity': 1
}

# Gesture thresholds
GESTURE_THRESHOLDS = {
    'pinch_distance': 0.05,
    'fingers_apart_distance': 0.07,
    'namaste_distance': 0.1
}

# System control settings
SYSTEM_CONFIG = {
    'brightness_step': 10,
    'volume_step': 0.05,
    'scroll_step': 0.5
} 