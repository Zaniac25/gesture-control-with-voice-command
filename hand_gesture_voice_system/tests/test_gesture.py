"""
Gesture Recognition Test Suite
Unit and integration tests for gesture recognition functionality
"""

import unittest
import cv2
import numpy as np
import mediapipe as mp
from modules.gesture_recognition import GestureRecognizer
from modules.utils import DataCollector
import os

class TestGestureRecognition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize test resources"""
        # Create test data directory
        os.makedirs('tests/test_data', exist_ok=True)
        
        # Initialize MediaPipe hands for generating test data
        cls.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.8
        )
        
        # Sample test images
        cls.test_images = {
            'fist': 'tests/test_data/fist.jpg',
            'palm': 'tests/test_data/palm.jpg',
            'thumbs_up': 'tests/test_data/thumbs_up.jpg'
        }
        
        # Generate test data if not exists
        if not all(os.path.exists(img) for img in cls.test_images.values()):
            cls._generate_test_images()

    @classmethod
    def _generate_test_images(cls):
        """Create sample test images with hand landmarks"""
        # Create colored blank images
        for gesture, path in cls.test_images.items():
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            img[:] = (50, 50, 50)  # Gray background
            cv2.imwrite(path, img)
        print("Generated test images")

    def setUp(self):
        """Initialize fresh recognizer for each test"""
        self.recognizer = GestureRecognizer()
        self.data_collector = DataCollector(data_dir='tests/test_data')

    def test_01_recognizer_initialization(self):
        """Test gesture recognizer initializes properly"""
        self.assertIsNotNone(self.recognizer.hands)
        self.assertIsNotNone(self.recognizer.classifier)
        self.assertGreater(len(self.recognizer.gesture_labels), 0)

    def test_02_hand_detection(self):
        """Test hand detection in sample images"""
        for gesture, img_path in self.test_images.items():
            with self.subTest(gesture=gesture):
                frame = cv2.imread(img_path)
                result = self.recognizer.process_frame(frame)
                self.assertTrue(result['hand_detected'])

    def test_03_gesture_classification(self):
        """Test gesture classification with synthetic landmarks"""
        # Create synthetic test data
        test_cases = [
            ('fist', [0.1, 0.1, 0] * 21),  # All landmarks close
            ('palm', [0.5, 0.5, 0] * 21),   # Spread out landmarks
            ('point', [0.1, 0.1, 0] * 8 + [0.5, 0.5, 0] + [0.1, 0.1, 0] * 12)  # Extended index
        ]
        
        for gesture, landmarks in test_cases:
            with self.subTest(gesture=gesture):
                landmarks = np.array(landmarks).reshape(1, -1)
                pred, conf = self.recognizer.classify_gesture(landmarks)
                self.assertEqual(pred, gesture)
                self.assertGreater(conf, 0.7)

    def test_04_data_collection(self):
        """Test data collection functionality"""
        sample_data = np.random.rand(63)  # 21 landmarks * 3 coordinates
        self.data_collector.add_sample(sample_data, 'test_gesture')
        self.assertEqual(len(self.data_collector.gesture_data), 1)
        self.assertEqual(len(self.data_collector.labels), 1)
        
        # Test saving
        self.data_collector.save_data()
        self.assertTrue(os.path.exists('tests/test_data/labels.txt'))

    def test_05_frame_processing_latency(self):
        """Test frame processing meets performance requirements"""
        test_frame = cv2.imread(self.test_images['palm'])
        
        # Warm up
        for _ in range(5):
            self.recognizer.process_frame(test_frame)
        
        # Time 100 iterations
        import time
        start = time.time()
        for _ in range(100):
            self.recognizer.process_frame(test_frame)
        elapsed = time.time() - start
        
        fps = 100 / elapsed
        print(f"\nFrame processing rate: {fps:.1f} FPS")
        self.assertGreater(fps, 25)  # Minimum 25 FPS required

    def test_06_model_loading(self):
        """Test model loading fallback behavior"""
        # Backup original model
        original_model = self.recognizer.classifier
        
        # Test invalid model path
        with self.assertLogs(level='WARNING'):
            self.recognizer.load_model('invalid_path.pkl')
        
        # Should fall back to basic model
        self.assertIsNotNone(self.recognizer.classifier)
        
        # Restore original
        self.recognizer.classifier = original_model

    def test_07_gesture_smoothing(self):
        """Test gesture smoothing buffer"""
        test_gestures = ['fist', 'palm', 'fist', 'fist', 'palm']
        
        for gesture in test_gestures:
            smoothed = self.recognizer.smooth_gesture(gesture)
        
        # After 5 samples, should return most frequent
        self.assertEqual(smoothed, 'fist')

class GestureIntegrationTest(unittest.TestCase):
    """Integration tests with camera feed"""
    
    def test_live_gesture_recognition(self):
        """Test recognition with live camera (requires webcam)"""
        recognizer = GestureRecognizer()
        cap = cv2.VideoCapture(0)
        
        try:
            # Test for 5 seconds
            import time
            end_time = time.time() + 5
            detections = 0
            
            while time.time() < end_time:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                result = recognizer.process_frame(frame)
                if result['hand_detected']:
                    detections += 1
                    self.assertIn(result['gesture'], recognizer.gesture_labels.values())
            
            print(f"\nLive test detected {detections} frames with hands")
            self.assertGreater(detections, 10)  # Expect at least 10 detections in 5 sec
        finally:
            cap.release()

if __name__ == "__main__":
    unittest.main(
        failfast=False,
        buffer=True,
        verbosity=2
    )