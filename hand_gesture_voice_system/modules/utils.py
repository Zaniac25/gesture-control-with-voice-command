"""
Utilities Module
Common utility functions and classes for the gesture recognition system
"""

import logging
import time
import os
import json
import numpy as np
import cv2
from datetime import datetime

class Logger:
    """Custom logger for the system"""
    
    def __init__(self, log_file='logs/system.log'):
        self.logger = logging.getLogger('GestureVoiceSystem')
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)

class DataCollector:
    """Data collection utility for training gesture models"""
    
    def __init__(self, data_dir='models/training_data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.gesture_data = []
        self.labels = []
    
    def add_sample(self, landmarks, label):
        """Add a training sample"""
        self.gesture_data.append(landmarks)
        self.labels.append(label)
    
    def save_data(self):
        """Save collected data to files"""
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(self.gesture_data)
        df['label'] = self.labels
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(f"{self.data_dir}/gesture_data_{timestamp}.csv", index=False)
        
        # Save labels
        unique_labels = list(set(self.labels))
        with open(f"{self.data_dir}/labels.txt", 'w') as f:
            for label in unique_labels:
                f.write(f"{label}\n")

class ConfigManager:
    """Configuration management utility"""
    
    @staticmethod
    def load_commands():
        """Load voice commands from JSON file"""
        try:
            with open('config/commands.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    @staticmethod
    def save_commands(commands):
        """Save voice commands to JSON file"""
        with open('config/commands.json', 'w') as f:
            json.dump(commands, f, indent=4)

class PerformanceMonitor:
    """Monitor system performance"""
    
    def __init__(self):
        self.frame_times = []
        self.gesture_counts = {}
        self.voice_counts = {}
    
    def log_frame_time(self, frame_time):
        """Log frame processing time"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 100:
            self.frame_times.pop(0)
    
    def log_gesture(self, gesture):
        """Log detected gesture"""
        self.gesture_counts[gesture] = self.gesture_counts.get(gesture, 0) + 1
    
    def log_voice_command(self, command):
        """Log voice command"""
        self.voice_counts[command] = self.voice_counts.get(command, 0) + 1
    
    def get_fps(self):
        """Calculate average FPS"""
        if not self.frame_times:
            return 0
        return 1.0 / np.mean(self.frame_times)
    
    def get_stats(self):
        """Get performance statistics"""
        return {
            'fps': self.get_fps(),
            'gesture_counts': self.gesture_counts,
            'voice_counts': self.voice_counts
        }

def draw_landmarks(image, landmarks, connections=None, color=(0, 255, 0), thickness=2):
    """Utility function to draw landmarks on an image"""
    image = image.copy()
    for landmark in landmarks:
        x = int(landmark.x * image.shape[1])
        y = int(landmark.y * image.shape[0])
        cv2.circle(image, (x, y), thickness, color, -1)
    
    if connections:
        for connection in connections:
            start = connection[0]
            end = connection[1]
            x1 = int(landmarks[start].x * image.shape[1])
            y1 = int(landmarks[start].y * image.shape[0])
            x2 = int(landmarks[end].x * image.shape[1])
            y2 = int(landmarks[end].y * image.shape[0])
            cv2.line(image, (x1, y1), (x2, y2), color, thickness)
    
    return image

def normalize_landmarks(landmarks, image_shape):
    """Normalize landmarks to be invariant to image size"""
    normalized = []
    for lm in landmarks:
        normalized.extend([lm.x / image_shape[1], 
                         lm.y / image_shape[0], 
                         lm.z / image_shape[1]])  # Using width as z reference
    return np.array(normalized)