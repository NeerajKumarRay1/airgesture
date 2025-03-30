import mediapipe as mp
import numpy as np
import logging
from config import *
import cv2

class GestureDetector:
    def __init__(self, profile="Default"):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            model_complexity=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.profile = profile
        self.settings = GESTURE_PROFILES[profile]
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        self.logger.addHandler(handler)

    def detect_hands(self, image_rgb):
        """Process the image and return hand landmarks."""
        try:
            results = self.hands.process(image_rgb)
            if results.multi_hand_landmarks:
                return list(zip(results.multi_hand_landmarks, results.multi_handedness))
            return []
        except Exception as e:
            self.logger.error(f"Error detecting hands: {str(e)}")
            return []

    def is_two_fingers_up(self, hand_landmarks):
        """Detect if index and middle fingers are up while others are down."""
        try:
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
            middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
            ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
            pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
            return index_tip < index_pip and middle_tip < middle_pip and ring_tip > middle_tip and pinky_tip > middle_tip
        except Exception as e:
            self.logger.error(f"Error detecting two fingers up: {str(e)}")
            return False

    def is_pinch(self, hand_landmarks):
        """Detect pinch gesture between thumb and index finger."""
        try:
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
            distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                   np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
            return distance < self.settings['pinch_threshold']
        except Exception as e:
            self.logger.error(f"Error detecting pinch: {str(e)}")
            return False

    def is_palm_up(self, hand_landmarks):
        """Detect if palm is facing up."""
        try:
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
            ring_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_MCP]
            
            # Check if palm is facing up (z-coordinate of MCPs should be less than wrist)
            palm_up = (
                middle_mcp.z < wrist.z and
                index_mcp.z < wrist.z and
                ring_mcp.z < wrist.z
            )
            
            # Also check if fingers are extended
            fingers_extended = self.is_five_fingers_up(hand_landmarks)
            
            return palm_up and fingers_extended
        except Exception as e:
            self.logger.error(f"Error detecting palm up: {str(e)}")
            return False

    def is_palm_down(self, hand_landmarks):
        """Detect if palm is facing down."""
        try:
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
            ring_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_MCP]
            
            # Check if palm is facing down (z-coordinate of MCPs should be greater than wrist)
            palm_down = (
                middle_mcp.z > wrist.z and
                index_mcp.z > wrist.z and
                ring_mcp.z > wrist.z
            )
            
            # Also check if fingers are extended
            fingers_extended = self.is_five_fingers_up(hand_landmarks)
            
            return palm_down and fingers_extended
        except Exception as e:
            self.logger.error(f"Error detecting palm down: {str(e)}")
            return False

    def is_middle_thumb_tap(self, hand_landmarks):
        """Detect middle finger and thumb tap."""
        try:
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
            distance = np.linalg.norm(np.array([middle_tip.x, middle_tip.y, middle_tip.z]) - 
                                   np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
            return distance < self.settings['pinch_threshold']
        except Exception as e:
            self.logger.error(f"Error detecting middle thumb tap: {str(e)}")
            return False

    def is_fingers_apart(self, hand_landmarks):
        """Detect if index and middle fingers are apart."""
        try:
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                   np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
            return distance > self.settings['finger_distance_threshold']
        except Exception as e:
            self.logger.error(f"Error detecting fingers apart: {str(e)}")
            return False

    def is_five_fingers_up(self, hand_landmarks):
        """Detect if all fingers are up."""
        try:
            return all(hand_landmarks.landmark[finger].y < hand_landmarks.landmark[finger - 2].y 
                      for finger in [self.mp_hands.HandLandmark.INDEX_FINGER_TIP, 
                                   self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                                   self.mp_hands.HandLandmark.RING_FINGER_TIP, 
                                   self.mp_hands.HandLandmark.PINKY_TIP])
        except Exception as e:
            self.logger.error(f"Error detecting five fingers up: {str(e)}")
            return False

    def is_five_fingers_down(self, hand_landmarks):
        """Detect if all fingers are down."""
        try:
            return all(hand_landmarks.landmark[finger].y > hand_landmarks.landmark[finger - 2].y 
                      for finger in [self.mp_hands.HandLandmark.INDEX_FINGER_TIP, 
                                   self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                                   self.mp_hands.HandLandmark.RING_FINGER_TIP, 
                                   self.mp_hands.HandLandmark.PINKY_TIP])
        except Exception as e:
            self.logger.error(f"Error detecting five fingers down: {str(e)}")
            return False

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
        return (pinky_tip > pinky_pip and 
                index_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                middle_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                ring_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and
                thumb_tip > hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP].y)

    def is_index_middle_fingers_together(self, hand_landmarks):
        """Detect if index and middle fingers are together."""
        try:
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                   np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
            return distance < self.settings['pinch_threshold']
        except Exception as e:
            self.logger.error(f"Error detecting fingers together: {str(e)}")
            return False

    def is_full_palm_open(self, hand_landmarks):
        """Detect if all fingers are extended."""
        try:
            return self.is_five_fingers_up(hand_landmarks)
        except Exception as e:
            self.logger.error(f"Error detecting full palm open: {str(e)}")
            return False

    def is_index_finger_up(self, hand_landmarks):
        """Detect if index finger is up and other fingers are down."""
        try:
            # Get only the landmarks we need
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
            
            # Simplified checks for better performance
            index_up = index_tip.y < index_pip.y
            other_fingers_down = (middle_tip.y > index_pip.y and 
                                ring_tip.y > index_pip.y and 
                                pinky_tip.y > index_pip.y)
            
            return index_up and other_fingers_down
        except Exception as e:
            self.logger.error(f"Error detecting index finger up: {str(e)}")
            return False

    def is_namaste_gesture(self, hand_landmarks1, hand_landmarks2):
        """Detect if hands are in namaste position."""
        try:
            wrist1 = hand_landmarks1.landmark[self.mp_hands.HandLandmark.WRIST]
            wrist2 = hand_landmarks2.landmark[self.mp_hands.HandLandmark.WRIST]
            distance = np.linalg.norm(
                np.array([wrist1.x, wrist1.y]) - 
                np.array([wrist2.x, wrist2.y])
            )
            return distance < 0.1
        except Exception as e:
            self.logger.error(f"Error detecting namaste gesture: {str(e)}")
            return False

    def change_profile(self, profile_name):
        """Change the current gesture profile."""
        if profile_name.title() in GESTURE_PROFILES:
            self.profile = profile_name.title()
            self.settings = GESTURE_PROFILES[self.profile]
            self.logger.info(f"Changed to profile: {self.profile}")
            return True
        self.logger.warning(f"Profile {profile_name} not found")
        return False 

    def process_frame(self, frame):
        """Process a frame and return detected gestures with their hand landmarks."""
        try:
            # Only process every other frame for better performance
            if not hasattr(self, '_frame_counter'):
                self._frame_counter = 0
            self._frame_counter += 1
            if self._frame_counter % 2 != 0:
                return None

            # Resize frame for faster processing
            frame = cv2.resize(frame, (640, 480))
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image_rgb)
            
            if not results.multi_hand_landmarks:
                return None
                
            gesture_data = []
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_type = "Right" if handedness.classification[0].label == "Right" else "Left"
                
                # Check all gestures in order of priority
                if self.is_index_finger_up(hand_landmarks):
                    gesture_data.append((f"Index up - {hand_type} hand", hand_landmarks))
                elif self.is_pinch(hand_landmarks):
                    gesture_data.append((f"Pinch - {hand_type} hand", hand_landmarks))
                elif self.is_middle_thumb_tap(hand_landmarks):
                    gesture_data.append((f"Middle thumb tap - {hand_type} hand", hand_landmarks))
                elif self.is_two_fingers_up(hand_landmarks):
                    gesture_data.append((f"Two fingers up - {hand_type} hand", hand_landmarks))
                elif self.is_two_fingers_down(hand_landmarks):
                    gesture_data.append((f"Two fingers down - {hand_type} hand", hand_landmarks))
                elif self.is_five_fingers_up(hand_landmarks):
                    gesture_data.append((f"Five fingers up - {hand_type} hand", hand_landmarks))
                elif self.is_five_fingers_down(hand_landmarks):
                    gesture_data.append((f"Five fingers down - {hand_type} hand", hand_landmarks))
                    
            return gesture_data if gesture_data else None
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return None

    def is_two_fingers_down(self, hand_landmarks):
        """Detect if index and middle fingers are down while others are up."""
        try:
            # Get finger landmarks
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
            ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            
            # Check if index and middle fingers are down (tips below pips)
            index_down = index_tip.y > index_pip.y and index_tip.y > wrist.y
            middle_down = middle_tip.y > middle_pip.y and middle_tip.y > wrist.y
            
            # Check if other fingers are up
            ring_up = ring_tip.y < middle_pip.y
            pinky_up = pinky_tip.y < middle_pip.y
            
            return index_down and middle_down and ring_up and pinky_up
        except Exception as e:
            self.logger.error(f"Error detecting two fingers down: {str(e)}")
            return False

    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on the frame."""
        self.mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        ) 

    def is_three_fingers_up(self, hand_landmarks):
        """Detect if index, middle, and ring fingers are up while others are down."""
        try:
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
            middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
            ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
            ring_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y
            pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
            
            return (index_tip < index_pip and 
                   middle_tip < middle_pip and 
                   ring_tip < ring_pip and 
                   pinky_tip > ring_tip)
        except Exception as e:
            self.logger.error(f"Error detecting three fingers up: {str(e)}")
            return False
            
    def is_three_fingers_down(self, hand_landmarks):
        """Detect if index, middle, and ring fingers are down."""
        try:
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
            middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
            ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
            ring_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y
            
            return (index_tip > index_pip and 
                   middle_tip > middle_pip and 
                   ring_tip > ring_pip)
        except Exception as e:
            self.logger.error(f"Error detecting three fingers down: {str(e)}")
            return False 