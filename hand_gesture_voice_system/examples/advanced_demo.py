"""
Advanced Demo Script
Demonstrates enhanced gesture recognition, voice commands, and system integration
"""

import cv2
import numpy as np
import mediapipe as mp
import speech_recognition as sr
import pyttsx3
import threading
import time
import pyautogui
import webbrowser
from datetime import datetime

class AdvancedDemo:
    def __init__(self):
        """Initialize advanced demo with full system capabilities"""
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Voice setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)
        
        # System state
        self.current_gesture = "none"
        self.last_voice_command = "none"
        self.listening = True
        self.gesture_buffer = []
        self.voice_command_history = []
        self.action_history = []
        
        # Virtual mouse control
        self.mouse_active = False
        self.prev_index_tip = None
        
        # Gesture recognition model (simple version)
        self.gesture_labels = {
            0: 'fist', 1: 'palm', 2: 'thumbs_up', 
            3: 'peace', 4: 'ok', 5: 'point'
        }
        
        # Start system threads
        self.start_threads()
    
    def start_threads(self):
        """Start all system threads"""
        # Voice processing thread
        self.voice_thread = threading.Thread(target=self.voice_processing_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        # System monitoring thread
        self.monitor_thread = threading.Thread(target=self.system_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def voice_processing_loop(self):
        """Advanced voice command processing"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=3, 
                        phrase_time_limit=5
                    )
                    command = self.recognizer.recognize_google(audio).lower()
                    self.last_voice_command = command
                    self.voice_command_history.append(
                        f"{datetime.now().strftime('%H:%M:%S')}: {command}"
                    )
                    
                    self.process_voice_command(command)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.speak("Could not understand audio")
                except Exception as e:
                    print(f"Voice processing error: {e}")
    
    def process_voice_command(self, command):
        """Execute actions based on voice commands"""
        command = command.lower()
        
        # System control commands
        if any(word in command for word in ["hello", "hi", "hey"]):
            self.speak("Hello! How can I help you?")
        
        elif "goodbye" in command or "exit" in command:
            self.speak("Goodbye! Shutting down system.")
            self.listening = False
            
        # Application control
        elif "open browser" in command:
            webbrowser.open("https://google.com")
            self.action_history.append("Opened browser")
            
        elif "close browser" in command:
            pyautogui.hotkey('alt', 'f4')
            self.action_history.append("Closed browser")
            
        # Media control
        elif "volume up" in command:
            pyautogui.press('volumeup')
            self.action_history.append("Volume increased")
            
        elif "volume down" in command:
            pyautogui.press('volumedown')
            self.action_history.append("Volume decreased")
            
        elif "mute" in command:
            pyautogui.press('volumemute')
            self.action_history.append("Audio muted")
            
        # Mouse control
        elif "enable mouse" in command:
            self.mouse_active = True
            self.speak("Virtual mouse enabled")
            
        elif "disable mouse" in command:
            self.mouse_active = False
            self.speak("Virtual mouse disabled")
            
        # Special functions
        elif "take screenshot" in command:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pyautogui.screenshot(f"screenshot_{timestamp}.png")
            self.speak("Screenshot saved")
            self.action_history.append(f"Screenshot taken at {timestamp}")
            
        else:
            self.speak("Command not recognized")
    
    def detect_complex_gesture(self, hand_landmarks):
        """Advanced gesture recognition with virtual mouse control"""
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
        
        # Thumb and finger tips
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Calculate distances between fingers
        thumb_index_dist = np.linalg.norm(thumb_tip - index_tip)
        index_middle_dist = np.linalg.norm(index_tip - middle_tip)
        
        # Virtual mouse control
        if self.mouse_active:
            screen_width, screen_height = pyautogui.size()
            mouse_x = int(index_tip[0] * screen_width)
            mouse_y = int(index_tip[1] * screen_height)
            
            if self.prev_index_tip is not None:
                # Smooth mouse movement
                smooth_x = int(0.5 * mouse_x + 0.5 * self.prev_index_tip[0])
                smooth_y = int(0.5 * mouse_y + 0.5 * self.prev_index_tip[1])
                pyautogui.moveTo(smooth_x, smooth_y, duration=0.1)
            
            self.prev_index_tip = (mouse_x, mouse_y)
            
            # Click detection (thumb and index finger pinch)
            if thumb_index_dist < 0.05:
                pyautogui.click()
                return "click"
        
        # Gesture recognition
        if thumb_index_dist < 0.05 and np.linalg.norm(thumb_tip - middle_tip) > 0.1:
            return "ok"
        elif index_middle_dist < 0.05 and np.linalg.norm(index_tip - ring_tip) < 0.05:
            return "peace"
        elif landmarks[4][1] < landmarks[3][1] and all(lm[1] > landmarks[0][1] for lm in landmarks[5:]):
            return "thumbs_up"
        elif all(lm[1] < landmarks[0][1] for lm in landmarks[5:]):
            return "palm"
        elif all(lm[1] > landmarks[0][1] for lm in landmarks[5:]):
            return "fist"
        elif landmarks[8][1] < landmarks[0][1] and all(lm[1] > landmarks[0][1] for lm in landmarks[9:]):
            return "point"
        
        return "none"
    
    def process_gesture(self, gesture):
        """Execute actions based on gestures"""
        if gesture == "click":
            return  # Already handled in detection
        
        self.gesture_buffer.append(gesture)
        if len(self.gesture_buffer) > 5:
            self.gesture_buffer.pop(0)
        
        # Get most frequent gesture in buffer
        stable_gesture = max(set(self.gesture_buffer), key=self.gesture_buffer.count)
        
        if stable_gesture == "thumbs_up":
            pyautogui.press('volumeup')
            self.action_history.append("Volume up (gesture)")
        elif stable_gesture == "ok":
            pyautogui.press('volumedown')
            self.action_history.append("Volume down (gesture)")
        elif stable_gesture == "peace":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pyautogui.screenshot(f"screenshot_{timestamp}.png")
            self.action_history.append(f"Screenshot (gesture) at {timestamp}")
        elif stable_gesture == "point" and not self.mouse_active:
            self.speak("Say 'enable mouse' to activate virtual mouse")
    
    def system_monitor(self):
        """Monitor system status and performance"""
        while self.listening:
            time.sleep(5)
            if len(self.action_history) > 10:
                self.action_history = self.action_history[-10:]
            if len(self.voice_command_history) > 10:
                self.voice_command_history = self.voice_command_history[-10:]
    
    def speak(self, text):
        """Advanced text-to-speech with queuing"""
        def speak_task():
            self.tts.say(text)
            self.tts.runAndWait()
        
        threading.Thread(target=speak_task, daemon=True).start()
    
    def run_demo(self):
        """Run the advanced demo"""
        print("Advanced Gesture and Voice Control System")
        print("Available voice commands:")
        print("- 'open/close browser' - Control web browser")
        print("- 'volume up/down/mute' - Adjust audio")
        print("- 'enable/disable mouse' - Virtual mouse control")
        print("- 'take screenshot' - Capture screen")
        print("- 'goodbye' - Exit system")
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
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
                    gesture = self.detect_complex_gesture(hand_landmarks)
                    if gesture != "none":
                        self.current_gesture = gesture
                        self.process_gesture(gesture)
            else:
                self.current_gesture = "none"
                self.prev_index_tip = None
            
            # Display information
            self.draw_ui_overlay(frame)
            
            cv2.imshow('Advanced Demo', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.listening = False
        
        cap.release()
        cv2.destroyAllWindows()
    
    def draw_ui_overlay(self, frame):
        """Draw comprehensive UI overlay"""
        # System status
        status_y = 30
        cv2.putText(frame, f"Gesture: {self.current_gesture}", (10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        status_y += 30
        cv2.putText(frame, f"Last Command: {self.last_voice_command[:30]}", (10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
        status_y += 25
        cv2.putText(frame, f"Virtual Mouse: {'ON' if self.mouse_active else 'OFF'}", (10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        
        # Instructions
        cv2.putText(frame, "Say 'enable mouse' for virtual mouse", (10, frame.shape[0] - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Press Q or say 'goodbye' to exit", (10, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

if __name__ == "__main__":
    demo = AdvancedDemo()
    demo.run_demo()