"""
Hand Gesture Recognition with Voice Commands System
A comprehensive system for controlling computer functions using hand gestures and voice commands
Author: [Your Name]
College Project - Computer Science
"""

import cv2
import threading
import time
from modules.gesture_recognition import GestureRecognizer
from modules.voice_commands import VoiceCommandHandler
from modules.system_controller import SystemController
from modules.utils import Logger
from config.settings import *

class HandGestureVoiceSystem:
    def __init__(self):
        """Initialize the complete system"""
        self.logger = Logger()
        self.gesture_recognizer = GestureRecognizer()
        self.voice_handler = VoiceCommandHandler()
        self.system_controller = SystemController()
        
        # System state
        self.running = False
        self.gesture_thread = None
        self.voice_thread = None
        
        # Initialize camera
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        
        self.logger.info("System initialized successfully")
    
    def start_system(self):
        """Start the gesture recognition and voice command system"""
        self.running = True
        
        # Start gesture recognition thread
        self.gesture_thread = threading.Thread(target=self.gesture_loop)
        self.gesture_thread.daemon = True
        self.gesture_thread.start()
        
        # Start voice command thread
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        self.logger.info("System started - both gesture and voice recognition active")
        
        # Main display loop
        self.display_loop()
    
    def gesture_loop(self):
        """Main gesture recognition loop"""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process gesture
            gesture_result = self.gesture_recognizer.process_frame(frame)
            
            if gesture_result['gesture'] != 'none':
                self.system_controller.execute_gesture_command(gesture_result)
                self.logger.info(f"Gesture detected: {gesture_result['gesture']}")
            
            # Add gesture info to frame
            self.add_gesture_info(frame, gesture_result)
            
            # Display frame
            cv2.imshow('Hand Gesture Recognition', frame)
            
            # Break on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_system()
                break
    
    def voice_loop(self):
        """Voice command processing loop"""
        while self.running:
            try:
                command = self.voice_handler.listen_for_command()
                if command:
                    self.system_controller.execute_voice_command(command)
                    self.logger.info(f"Voice command: {command}")
            except Exception as e:
                self.logger.error(f"Voice processing error: {e}")
            
            time.sleep(0.1)
    
    def display_loop(self):
        """Main display and UI loop"""
        while self.running:
            # Handle any UI updates or system monitoring
            time.sleep(0.1)
    
    def add_gesture_info(self, frame, gesture_result):
        """Add gesture information overlay to frame"""
        # Display current gesture
        cv2.putText(frame, f"Gesture: {gesture_result['gesture']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display confidence
        cv2.putText(frame, f"Confidence: {gesture_result['confidence']:.2f}", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Display instructions
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def stop_system(self):
        """Stop the system gracefully"""
        self.running = False
        
        if self.gesture_thread:
            self.gesture_thread.join()
        if self.voice_thread:
            self.voice_thread.join()
            
        self.cap.release()
        cv2.destroyAllWindows()
        self.logger.info("System stopped")

def main():
    """Main function"""
    print("="*50)
    print("Hand Gesture Recognition with Voice Commands")
    print("College Project - Computer Science")
    print("="*50)
    
    try:
        system = HandGestureVoiceSystem()
        system.start_system()
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()