"""Configuration settings for the Air Gesture Control application."""

import logging

# Logging configuration
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'air_gesture.log',
    'filemode': 'a'
}

# Camera configuration
CAMERA_CONFIG = {
    'width': 640,
    'height': 480,
    'fps': 30
}

# Gesture detection configuration
GESTURE_CONFIG = {
    'max_num_hands': 2,
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.5,
    'model_complexity': 1,
    'cursor_smoothing': 0.5,
    'palm_open_cooldown': 1.0  # seconds
}

# Gesture threshold values
GESTURE_THRESHOLDS = {
    'pinch_distance': 0.05,
    'fingers_apart_distance': 0.08,
    'fingers_together_distance': 0.04,
    'namaste_distance': 0.15
}

# System control configuration
SYSTEM_CONFIG = {
    'brightness_step': 5,  # percentage
    'volume_step': 0.05,   # 0-1 scale
    'scroll_step': 2      # lines
} 