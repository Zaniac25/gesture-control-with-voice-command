"""
Integration Test Suite
Tests the complete gesture-voice system interaction
"""

import unittest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from modules.gesture_recognition import GestureRecognizer
from modules.voice_commands import VoiceCommandHandler
from modules.system_controller import SystemController
from modules.utils import Logger
import mediapipe as mp
import pyautogui

class TestSystemIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize shared test resources"""
        cls.logger = Logger(log_file='tests/test_integration.log')
        
        # Create test image with hand landmarks
        cls.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cls._add_mock_landmarks(cls.test_frame)
        
        # Initialize real components with test config
        cls.recognizer = GestureRecognizer()
        cls.voice_handler = VoiceCommandHandler()
        cls.controller = SystemController()

    @classmethod
    def _add_mock_landmarks(cls, frame):
        """Add synthetic hand landmarks to test frame"""
        # Simulate MediaPipe output structure
        landmark = mp.solutions.hands.HandLandmark
        connections = mp.solutions.hands.HAND_CONNECTIONS
        
        # Draw fake landmarks (simplified hand)
        h, w = frame.shape[:2]
        for i in range(21):
            x = int(w * (0.5 + 0.1 * (i % 3)))
            y = int(h * (0.3 + 0.02 * i))
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
        
        return frame

    def setUp(self):
        """Reset mocks before each test"""
        self.recognizer.classifier = MagicMock()
        self.recognizer.classifier.predict.return_value = [0]  # Fist gesture
        self.recognizer.classifier.predict_proba.return_value = [[0.9, 0.1, 0, 0, 0, 0]]
        
        # Patch pyautogui to prevent real actions
        self.patcher = patch.object(pyautogui, 'hotkey')
        self.mock_hotkey = self.patcher.start()

    def tearDown(self):
        """Clean up after each test"""
        self.patcher.stop()

    def test_01_gesture_to_action(self):
        """Test complete gesture-to-action pipeline"""
        # Process test frame
        result = self.recognizer.process_frame(self.test_frame)
        
        # Verify detection
        self.assertTrue(result['hand_detected'])
        self.assertEqual(result['gesture'], 'fist')
        
        # Execute action
        self.controller.execute_gesture_command(result)
        
        # Verify action (fist should trigger close_application)
        self.mock_hotkey.assert_called_with('alt', 'f4')

    @patch('modules.voice_commands.VoiceCommandHandler.listen_for_command')
    def test_02_voice_to_action(self, mock_listen):
        """Test complete voice-to-action pipeline"""
        # Setup mock voice command
        mock_listen.return_value = 'volume_up'
        
        # Process command
        command = self.voice_handler.listen_for_command()
        self.controller.execute_voice_command(command)
        
        # Verify action
        pyautogui.press.assert_called_with('volumeup')

    @patch('modules.voice_commands.VoiceCommandHandler.listen_for_command')
    def test_03_simultaneous_gesture_and_voice(self, mock_listen):
        """Test combined gesture and voice processing"""
        # Setup mocks
        mock_listen.return_value = 'open_browser'
        
        # Process both inputs
        gesture_result = self.recognizer.process_frame(self.test_frame)
        voice_command = self.voice_handler.listen_for_command()
        
        # Execute both actions
        self.controller.execute_gesture_command(gesture_result)
        self.controller.execute_voice_command(voice_command)
        
        # Verify both executed
        self.mock_hotkey.assert_called_once()  # Gesture action
        webbrowser.open.assert_called_with('https://www.google.com')

    def test_04_action_cooldown(self):
        """Test action rate limiting"""
        # First execution
        self.controller.execute_voice_command('volume_up')
        pyautogui.press.assert_called_with('volumeup')
        
        # Immediate second execution should be blocked
        pyautogui.press.reset_mock()
        self.controller.execute_voice_command('volume_up')
        pyautogui.press.assert_not_called()

    @patch('modules.gesture_recognition.GestureRecognizer.process_frame')
    def test_05_gesture_smoothing(self, mock_process):
        """Test gesture smoothing across frames"""
        # Setup mock frame processor with varying results
        mock_process.side_effect = [
            {'gesture': 'fist', 'confidence': 0.9, 'hand_detected': True},
            {'gesture': 'palm', 'confidence': 0.8, 'hand_detected': True},
            {'gesture': 'fist', 'confidence': 0.85, 'hand_detected': True},
            {'gesture': 'fist', 'confidence': 0.95, 'hand_detected': True}
        ]
        
        # Process sequence
        results = []
        for _ in range(4):
            results.append(self.recognizer.process_frame(None))
            smoothed = self.recognizer.smooth_gesture(results[-1]['gesture'])
        
        # Verify stabilization
        self.assertEqual(smoothed, 'fist')

    def test_06_error_handling(self):
        """Test system resilience to errors"""
        # Force classifier error
        self.recognizer.classifier.predict.side_effect = Exception("Test error")
        
        # Should handle gracefully
        result = self.recognizer.process_frame(self.test_frame)
        self.assertEqual(result['gesture'], 'none')
        self.assertEqual(result['confidence'], 0.0)

class HardwareIntegrationTest(unittest.TestCase):
    """Tests requiring actual hardware (camera/mic)"""
    
    @unittest.skipUnless(os.getenv('TEST_HARDWARE'), "Requires camera")
    def test_live_gesture_pipeline(self):
        """Test full gesture pipeline with real camera"""
        recognizer = GestureRecognizer()
        controller = SystemController()
        
        cap = cv2.VideoCapture(0)
        try:
            # Process 10 frames
            detections = 0
            for _ in range(10):
                ret, frame = cap.read()
                if not ret:
                    continue
                
                result = recognizer.process_frame(frame)
                if result['hand_detected']:
                    controller.execute_gesture_command(result)
                    detections += 1
            
            self.assertGreater(detections, 3, 
                             "Expected at least 3 detections in 10 frames")
        finally:
            cap.release()

    @unittest.skipUnless(os.getenv('TEST_HARDWARE'), "Requires microphone")
    @patch('modules.system_controller.SystemController.execute_voice_command')
    def test_live_voice_pipeline(self, mock_execute):
        """Test full voice pipeline with real microphone"""
        handler = VoiceCommandHandler()
        
        # Process for 5 seconds
        import time
        end_time = time.time() + 5
        while time.time() < end_time:
            command = handler.listen_for_command()
            if command:
                mock_execute(command)
        
        mock_execute.assert_called()

if __name__ == "__main__":
    unittest.main(
        failfast=False,
        buffer=True,
        verbosity=2
    )