"""
Voice Command Test Suite
Unit and integration tests for voice command functionality
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from modules.voice_commands import VoiceCommandHandler
from modules.utils import ConfigManager
import speech_recognition as sr

class TestVoiceCommandHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize test resources"""
        # Create test config directory
        os.makedirs('tests/test_config', exist_ok=True)
        
        # Create test commands.json
        cls.test_commands = {
            "voice_commands": {
                "test command": "test_action",
                "open browser": "open_browser"
            },
            "settings": {
                "voice": {
                    "response_delay": 0.5
                }
            }
        }
        
        with open('tests/test_config/commands.json', 'w') as f:
            json.dump(cls.test_commands, f)

    def setUp(self):
        """Create fresh handler for each test"""
        self.handler = VoiceCommandHandler()
        # Override config path for tests
        self.handler.voice_commands = self.test_commands["voice_commands"]

    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.recognize_google')
    def test_01_command_recognition(self, mock_recognize, mock_listen):
        """Test successful command recognition"""
        # Setup mock
        mock_recognize.return_value = "test command"
        mock_listen.return_value = MagicMock()
        
        # Execute
        command = self.handler.listen_for_command()
        
        # Verify
        self.assertEqual(command, "test_action")
        mock_recognize.assert_called_once()

    @patch('speech_recognition.Recognizer.listen')
    def test_02_unknown_command(self, mock_listen):
        """Test unrecognized command handling"""
        with patch('speech_recognition.Recognizer.recognize_google', 
                  return_value="unknown command"):
            command = self.handler.listen_for_command()
            self.assertIsNone(command)

    def test_03_command_processing(self):
        """Test command processing logic"""
        test_cases = [
            ("please open browser", "open_browser"),
            ("could you open browser now", "open_browser"),
            ("unknown command", None)
        ]
        
        for phrase, expected in test_cases:
            with self.subTest(phrase=phrase):
                result = self.handler.process_command(phrase)
                self.assertEqual(result, expected)

    @patch('pyttsx3.init')
    def test_04_text_to_speech(self, mock_tts):
        """Test TTS functionality"""
        # Configure mock engine
        mock_engine = MagicMock()
        mock_tts.return_value = mock_engine
        
        # Create new handler with mock
        handler = VoiceCommandHandler()
        handler.tts_engine = mock_engine
        
        # Test speak
        handler.speak("Test message")
        
        # Verify
        mock_engine.say.assert_called_with("Test message")
        mock_engine.runAndWait.assert_called_once()

    @patch('modules.voice_commands.VoiceCommandHandler.speak')
    def test_05_voice_feedback_disabled(self, mock_speak):
        """Test voice feedback disabling"""
        # Disable feedback
        self.handler.voice_commands["settings"]["voice"]["enable_feedback"] = False
        
        self.handler.speak("Test")
        mock_speak.assert_not_called()

    def test_06_config_manager_integration(self):
        """Test loading commands from config"""
        # Use test config
        original_commands = ConfigManager.load_commands()
        ConfigManager.load_commands = lambda: self.test_commands
        
        try:
            handler = VoiceCommandHandler()
            self.assertEqual(handler.voice_commands, self.test_commands["voice_commands"])
        finally:
            # Restore original
            ConfigManager.load_commands = lambda: original_commands

    @patch('speech_recognition.Microphone')
    def test_07_microphone_initialization(self, mock_mic):
        """Test microphone setup"""
        mock_mic_instance = MagicMock()
        mock_mic.return_value = mock_mic_instance
        
        handler = VoiceCommandHandler()
        self.assertEqual(handler.microphone, mock_mic_instance)

    @patch('speech_recognition.Recognizer.listen')
    def test_08_audio_timeout(self, mock_listen):
        """Test audio input timeout handling"""
        mock_listen.side_effect = sr.WaitTimeoutError()
        
        command = self.handler.listen_for_command()
        self.assertIsNone(command)

class VoiceIntegrationTest(unittest.TestCase):
    """Integration tests with audio hardware"""
    
    @unittest.skipUnless(os.getenv('TEST_HARDWARE'), "Requires audio hardware")
    def test_live_audio_processing(self):
        """Test live audio processing (requires microphone)"""
        handler = VoiceCommandHandler()
        
        # Test with simulated audio (requires pytest-audio)
        try:
            import pytest_audio
            with pytest_audio.record('tests/test_data/test_audio.wav'):
                print("\nSpeak 'test command' now...")
                command = handler.listen_for_command()
                
            self.assertEqual(command, "test_action")
        except ImportError:
            self.skipTest("pytest-audio not available")

    def test_command_add_remove(self):
        """Test dynamic command management"""
        handler = VoiceCommandHandler()
        
        # Add new command
        handler.add_custom_command("new phrase", "new_action")
        self.assertEqual(handler.voice_commands["new phrase"], "new_action")
        
        # Test processing
        result = handler.process_command("please say new phrase")
        self.assertEqual(result, "new_action")

if __name__ == "__main__":
    unittest.main(
        failfast=False,
        buffer=True,
        verbosity=2
    )