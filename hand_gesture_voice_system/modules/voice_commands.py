"""
Voice Commands Module
Handles speech recognition and text-to-speech functionality
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
from config.settings import *

class VoiceCommandHandler:
    def __init__(self):
        """Initialize speech recognition and text-to-speech"""
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=MICROPHONE_INDEX)
        
        # Text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
        
        # Voice commands mapping
        self.voice_commands = {
            'open browser': 'open_browser',
            'close browser': 'close_browser',
            'volume up': 'volume_up',
            'volume down': 'volume_down',
            'mute': 'mute_audio',
            'unmute': 'unmute_audio',
            'take screenshot': 'screenshot',
            'open calculator': 'open_calculator',
            'open notepad': 'open_notepad',
            'minimize window': 'minimize_window',
            'maximize window': 'maximize_window',
            'switch window': 'alt_tab',
            'scroll up': 'scroll_up',
            'scroll down': 'scroll_down',
            'zoom in': 'zoom_in',
            'zoom out': 'zoom_out',
            'hello system': 'greeting',
            'goodbye system': 'goodbye'
        }
        
        # Calibrate microphone
        self.calibrate_microphone()
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Microphone calibration failed: {e}")
    
    def listen_for_command(self):
        """Listen for voice command"""
        try:
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=VOICE_TIMEOUT, 
                    phrase_time_limit=VOICE_PHRASE_TIME_LIMIT
                )
            
            # Recognize speech
            command = self.recognizer.recognize_google(audio).lower()
            return self.process_command(command)
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def process_command(self, spoken_text):
        """Process spoken text and return command"""
        for phrase, command in self.voice_commands.items():
            if phrase in spoken_text:
                return command
        return None
    
    def speak(self, text):
        """Convert text to speech"""
        if ENABLE_VOICE_FEEDBACK:
            def speak_thread():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak_thread)
            thread.daemon = True
            thread.start()
    
    def add_custom_command(self, phrase, command):
        """Add custom voice command"""
        self.voice_commands[phrase.lower()] = command