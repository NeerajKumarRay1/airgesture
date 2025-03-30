import numpy as np
import mediapipe as mp

class GestureDetector:
    def __init__(self, mp_hands):
        self.mp_hands = mp_hands

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
        distance = np.linalg.norm(np.array([index_tip.x, index_tip.y, index_tip.z]) - 
                                np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < 0.05

    def is_middle_thumb_tap(self, hand_landmarks):
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        distance = np.linalg.norm(np.array([middle_tip.x, middle_tip.y, middle_tip.z]) - 
                                np.array([thumb_tip.x, thumb_tip.y, thumb_tip.z]))
        return distance < self.thresholds['pinch_distance']
        
    def is_fingers_apart(self, hand_landmarks):
        # Add implementation
        pass
        
    def is_five_fingers_up(self, hand_landmarks):
        # Add implementation
        pass

    # Add other gesture detection methods here... 