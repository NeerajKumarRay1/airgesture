# Camera configuration
CAMERA_CONFIG = {
    'width': 1280,
    'height': 720,
    'fps': 30
}

# Gesture detection configuration
GESTURE_CONFIG = {
    'max_num_hands': 2,
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.5,
    'model_complexity': 1,
    'cursor_smoothing': 0.5,
    'palm_open_cooldown': 1.0
}

# System control configuration
SYSTEM_CONFIG = {
    'brightness_step': 5,
    'volume_step': 0.1,
    'scroll_step': 1
}

# Gesture thresholds
GESTURE_THRESHOLDS = {
    'pinch_distance': 0.05,
    'fingers_apart_distance': 0.1,
    'namaste_distance': 0.1
} 