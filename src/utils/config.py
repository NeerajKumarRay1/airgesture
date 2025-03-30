import logging
import os

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILE = 'air_gesture.log'

# UI configuration
WINDOW_TITLE = "Air Gesture Control"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Gesture detection settings
MIN_DETECTION_CONFIDENCE = 0.8
MIN_TRACKING_CONFIDENCE = 0.8
MAX_NUM_HANDS = 2
MODEL_COMPLEXITY = 1

# Cursor movement settings
SMOOTHING_FACTOR = 0.3
CLICK_COOLDOWN = 0.5  # seconds

# Volume and brightness control
VOLUME_STEP = 2
BRIGHTNESS_STEP = 5

# Scroll settings
SCROLL_AMOUNT = 100

# Gesture profiles
GESTURE_PROFILES = {
    'default': {
        'cursor_movement': 'index_finger',
        'click': 'pinch',
        'volume': 'pinky_up',
        'brightness': 'pinky_down',
        'scroll': 'five_fingers'
    },
    'alternative': {
        'cursor_movement': 'index_middle_together',
        'click': 'middle_thumb_tap',
        'volume': 'two_fingers_up',
        'brightness': 'two_fingers_down',
        'scroll': 'namaste'
    }
}

# Help message
HELP_MESSAGE = """
Air Gesture Control Help:

Right Hand Gestures:
- Index finger up: Move cursor
- Pinch fingers: Click
- Pinky up: Increase volume
- Pinky down: Decrease volume

Left Hand Gestures:
- Five fingers up: Scroll up
- Five fingers down: Scroll down
- Full palm open: Increase brightness
- All fingers down: Decrease brightness

Additional Gestures:
- Namaste (both hands): Reset all controls
- Two fingers up: Alternative volume control
- Two fingers down: Alternative brightness control

Tips:
1. Keep your hand steady for better cursor control
2. Make gestures clear and deliberate
3. Wait for visual feedback before repeating gestures
4. Use the Help button to view this message again
""" 