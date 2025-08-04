"""
Basic Demo Script
Simple demonstration of gesture and voice recognition
"""

import cv2
import numpy as np
import mediapipe as mp
import speech_recognition as sr
import pyttsx3
import threading
import time

class BasicDemo:
    def __init__(self):
        """Initialize basic demo"""
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Voice setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts = pyttsx3.init()
        
        # State
        self.current_gesture = "none"
        self.last_voice_command = "none"
        self.listening = True
    
    def detect_gesture(self, hand_landmarks):
        """Simple gesture detection"""
        # Get landmark positions
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append([lm.x, lm.y])
        
        landmarks = np.array(landmarks)
        
        # Simple rule-based gesture detection
        # Thumb tip and index tip
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Index MCP (base of fingers)
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        ring_mcp = landmarks[13]
        pinky_mcp = landmarks[17]
        
        # Count extended fingers
        fingers_up = 0
        
        # Thumb
        if thumb_tip[0] > landmarks[3][0]:
            fingers_up += 1
        
        # Other fingers
        if index_tip[1] < index_mcp[1]:
            fingers_up += 1
        if middle_tip[1] < middle_mcp[1]:
            fingers_up += 1
        if ring_tip[1] < ring_mcp[1]:
            fingers_up += 1
        if pinky_tip[1] < pinky_mcp[1]:
            fingers_up += 1
        
        # Determine gesture
        if fingers_up == 0:
            return "fist"
        elif fingers_up == 5:
            return "palm"
        elif fingers_up == 1:
            return "one"
        elif fingers_up == 2:
            return "two"
        elif fingers_up == 3:
            return "three"
        else:
            return "other"
    
    def voice_thread(self):
        """Voice recognition thread"""
        while self.listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                
                command = self.recognizer.recognize_google(audio).lower()
                self.last_voice_command = command
                
                # Simple voice responses
                if "hello" in command:
                    self.speak("Hello! I can see your gestures.")
                elif "goodbye" in command:
                    self.speak("Goodbye!")
                    self.listening = False
                
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except Exception as e:
                print(f"Voice error: {e}")
    
    def speak(self, text):
        """Text to speech"""
        def speak_thread():
            self.tts.say(text)
            self.tts.runAndWait()
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def run_demo(self):
        """Run the basic demo"""
        print("Basic Gesture and Voice Demo")
        print("Show your hand to the camera and try voice commands")
        print("Say 'goodbye' to exit")
        
        # Start voice thread
        voice_thread = threading.Thread(target=self.voice_thread)
        voice_thread.daemon = True
        voice_thread.start()
        
        cap = cv2.VideoCapture(0)
        
        while self.listening:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Process gestures
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    self.current_gesture = self.detect_gesture(hand_landmarks)
            else:
                self.current_gesture = "none"
            
            # Display information
            cv2.putText(frame, f"Gesture: {self.current_gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Voice: {self.last_voice_command}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, "Say 'goodbye' to exit", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Basic Demo', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    demo = BasicDemo()
    demo.run_demo()