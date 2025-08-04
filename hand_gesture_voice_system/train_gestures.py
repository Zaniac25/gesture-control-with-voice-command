"""
Gesture Training Script
Collects training data and trains gesture recognition model
"""

import os
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from modules.utils import Logger, DataCollector
from datetime import datetime

class GestureTrainer:
    def __init__(self):
        """Initialize gesture trainer with MediaPipe and data structures"""
        self.logger = Logger(log_file='logs/training.log')
        self.data_collector = DataCollector()
        
        # MediaPipe Hands configuration
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,  # Better for training data collection
            max_num_hands=1,         # Single hand for training
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture configuration
        self.gesture_labels = {
            0: 'fist',
            1: 'palm',
            2: 'thumbs_up',
            3: 'peace',
            4: 'ok',
            5: 'point',
            6: 'pinch',
            7: 'three_fingers'
        }
        
        # Training parameters
        self.samples_per_gesture = 200  # Samples to collect per gesture
        self.test_size = 0.2            # Train-test split ratio
        self.random_state = 42          # Random seed for reproducibility

    def collect_training_data(self):
        """Interactive data collection from webcam"""
        cap = cv2.VideoCapture(0)
        current_gesture = None
        collecting = False
        sample_count = 0
        
        # Create training data directory
        os.makedirs('models/training_data', exist_ok=True)
        
        # Display instructions
        print("\nGesture Training Mode")
        print("====================")
        print("Key Commands:")
        print("0-7: Select gesture to record")
        print("  s: Save collected data")
        print("  q: Quit training mode")
        print("\nCurrent Gestures:")
        for key, gesture in self.gesture_labels.items():
            print(f"  {key}: {gesture}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Display status
            status_text = f"Gesture: {current_gesture}" if current_gesture else "Press 0-7 to select gesture"
            cv2.putText(frame, status_text, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if collecting:
                cv2.putText(frame, f"COLLECTING: {sample_count}/{self.samples_per_gesture}", 
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Process hand landmarks
            if results.multi_hand_landmarks and collecting and current_gesture:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Extract and store landmarks
                    landmarks = self._extract_landmarks(hand_landmarks)
                    self.data_collector.add_sample(landmarks, current_gesture)
                    sample_count += 1
                    
                    # Display sample count
                    cv2.putText(frame, f"Samples: {len(self.data_collector.gesture_data)}", 
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    if sample_count >= self.samples_per_gesture:
                        collecting = False
                        print(f"\nCollected {self.samples_per_gesture} samples for {self.gesture_labels[current_gesture]}")
            
            cv2.imshow('Gesture Training', frame)
            key = cv2.waitKey(1) & 0xFF
            
            # Handle key presses
            if key == ord('q'):
                break
            elif key == ord('s'):
                self._save_training_data()
                print("Training data saved!")
            elif chr(key) in map(str, self.gesture_labels.keys()):
                current_gesture = int(chr(key))
                collecting = True
                sample_count = 0
                print(f"\nCollecting samples for: {self.gesture_labels[current_gesture]}")
        
        cap.release()
        cv2.destroyAllWindows()

    def _extract_landmarks(self, hand_landmarks):
        """Convert hand landmarks to normalized feature vector"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])  # 3D coordinates
        return np.array(landmarks)

    def _save_training_data(self):
        """Save collected data to disk"""
        if not self.data_collector.gesture_data:
            print("No training data to save!")
            return
        
        # Create DataFrame
        data = np.array(self.data_collector.gesture_data)
        labels = np.array(self.data_collector.labels)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df = pd.DataFrame(data)
        df['label'] = labels
        df.to_csv(f'models/training_data/gesture_data_{timestamp}.csv', index=False)
        
        # Save labels mapping
        with open(f'models/training_data/labels_{timestamp}.txt', 'w') as f:
            for label in set(labels):
                f.write(f"{label}:{self.gesture_labels[label]}\n")
        
        self.logger.info(f"Saved training data with {len(data)} samples")

    def train_model(self):
        """Train and evaluate gesture classification model"""
        # Load all training data
        data_files = [f for f in os.listdir('models/training_data') 
                     if f.startswith('gesture_data') and f.endswith('.csv')]
        
        if not data_files:
            raise FileNotFoundError("No training data found! Collect data first.")
        
        # Combine all training data
        dfs = []
        for file in data_files:
            df = pd.read_csv(f'models/training_data/{file}')
            dfs.append(df)
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Prepare features and labels
        X = combined_df.drop('label', axis=1).values
        y = combined_df['label'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state)
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            class_weight='balanced'
        )
        
        self.logger.info(f"Training model with {len(X_train)} samples...")
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=self.gesture_labels.values())
        
        print("\nModel Evaluation:")
        print(f"Accuracy: {accuracy:.2f}")
        print("Classification Report:")
        print(report)
        
        # Save model
        os.makedirs('models', exist_ok=True)
        with open('models/gesture_classifier.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        # Save class labels
        with open('models/gesture_labels.pkl', 'wb') as f:
            pickle.dump(self.gesture_labels, f)
        
        self.logger.info(f"Model saved with accuracy: {accuracy:.2f}")
        return model

def main():
    """Main training function"""
    print("Gesture Recognition Training")
    print("===========================")
    print("1. Collect training data")
    print("2. Train model")
    print("3. Full pipeline (collect + train)")
    
    trainer = GestureTrainer()
    choice = input("\nEnter choice (1-3): ")
    
    try:
        if choice == '1':
            trainer.collect_training_data()
        elif choice == '2':
            trainer.train_model()
        elif choice == '3':
            trainer.collect_training_data()
            trainer.train_model()
        else:
            print("Invalid choice!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("\nTraining session complete.")

if __name__ == "__main__":
    main()