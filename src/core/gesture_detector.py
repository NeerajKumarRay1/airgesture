import numpy as np
import mediapipe as mp
import logging

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8,
            model_complexity=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.logger = logging.getLogger(__name__)

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
        return distance < 0.05

    def is_middle_thumb_tap(self, hand_landmarks):
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        distance = np.linalg.norm(np.array([middle_tip.x, middle_tip.y, middle_tip.z]) - np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < 0.05

    def is_fingers_apart(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - np.array([middle_tip.x, middle_tip.y, middle_tip.z]))
        return distance > 0.07

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
        return distance < 0.1 