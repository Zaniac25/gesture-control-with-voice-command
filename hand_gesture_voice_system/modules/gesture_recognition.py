"""
Gesture Recognition Module
Handles hand tracking and gesture classification using MediaPipe and OpenCV
"""

import cv2
import numpy as np
import mediapipe as mp
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from config.settings import *

class GestureRecognizer:
    def __init__(self):
        """Initialize MediaPipe and gesture classifier"""
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Gesture classifier
        self.classifier = None
        self.load_model()
        
        # Gesture labels
        self.gesture_labels = {
            0: 'fist',
            1: 'palm',
            2: 'thumbs_up',
            3: 'peace',
            4: 'ok',
            5: 'point'
        }
        
        # Smoothing buffer
        self.gesture_buffer = []
        self.buffer_size = GESTURE_SMOOTHING
    
    def load_model(self):
        """Load pre-trained gesture classifier"""
        model_path = 'models/gesture_classifier.pkl'
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.classifier = pickle.load(f)
        else:
            # Create and train a basic model
            self.create_basic_model()
    
    def create_basic_model(self):
        """Create a basic gesture classifier"""
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        # Note: In a real implementation, you would train this with actual data
        
    def extract_landmarks(self, hand_landmarks):
        """Extract hand landmark features"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        return np.array(landmarks)
    
    def classify_gesture(self, landmarks):
        """Classify gesture from landmarks"""
        if self.classifier is None:
            return 'none', 0.0
        
        try:
            # Reshape for prediction
            features = landmarks.reshape(1, -1)
            prediction = self.classifier.predict(features)[0]
            confidence = np.max(self.classifier.predict_proba(features))
            
            if confidence > GESTURE_THRESHOLD:
                return self.gesture_labels.get(prediction, 'unknown'), confidence
            else:
                return 'none', confidence
        except:
            return 'none', 0.0
    
    def smooth_gesture(self, gesture):
        """Apply smoothing to gesture recognition"""
        self.gesture_buffer.append(gesture)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        
        # Return most common gesture in buffer
        if len(self.gesture_buffer) >= 3:
            return max(set(self.gesture_buffer), key=self.gesture_buffer.count)
        return gesture
    
    def process_frame(self, frame):
        """Process a single frame for gesture recognition"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_result = {
            'gesture': 'none',
            'confidence': 0.0,
            'landmarks': None,
            'hand_detected': False
        }
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Extract features and classify
                landmarks = self.extract_landmarks(hand_landmarks)
                gesture, confidence = self.classify_gesture(landmarks)
                
                # Apply smoothing
                smoothed_gesture = self.smooth_gesture(gesture)
                
                gesture_result.update({
                    'gesture': smoothed_gesture,
                    'confidence': confidence,
                    'landmarks': landmarks,
                    'hand_detected': True
                })
                
                break  # Process only first hand
        
        return gesture_result