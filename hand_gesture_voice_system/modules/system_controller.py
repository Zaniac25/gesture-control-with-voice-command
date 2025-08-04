"""
System Controller Module
Handles system actions triggered by gestures and voice commands
"""

import pyautogui
import subprocess
import time
import webbrowser
from modules.utils import Logger

class SystemController:
    def __init__(self):
        """Initialize system controller"""
        self.logger = Logger()
        
        # Gesture to action mapping
        self.gesture_actions = {
            'fist': self.close_application,
            'palm': self.stop_action,
            'thumbs_up': self.volume_up,
            'peace': self.take_screenshot,
            'ok': self.confirm_action,
            'point': self.mouse_click
        }
        
        # Voice command to action mapping
        self.voice_actions = {
            'open_browser': self.open_browser,
            'close_browser': self.close_browser,
            'volume_up': self.volume_up,
            'volume_down': self.volume_down,
            'mute_audio': self.mute_audio,
            'unmute_audio': self.unmute_audio,
            'screenshot': self.take_screenshot,
            'open_calculator': self.open_calculator,
            'open_notepad': self.open_notepad,
            'minimize_window': self.minimize_window,
            'maximize_window': self.maximize_window,
            'alt_tab': self.switch_window,
            'scroll_up': self.scroll_up,
            'scroll_down': self.scroll_down,
            'zoom_in': self.zoom_in,
            'zoom_out': self.zoom_out,
            'greeting': self.greeting,
            'goodbye': self.goodbye
        }
        
        # Prevent rapid repeated actions
        self.last_action_time = {}
        self.action_cooldown = 1.0  # seconds
    
    def can_execute_action(self, action_name):
        """Check if action can be executed (cooldown check)"""
        current_time = time.time()
        if action_name in self.last_action_time:
            if current_time - self.last_action_time[action_name] < self.action_cooldown:
                return False
        
        self.last_action_time[action_name] = current_time
        return True
    
    def execute_gesture_command(self, gesture_result):
        """Execute action based on gesture"""
        gesture = gesture_result['gesture']
        
        if gesture in self.gesture_actions and self.can_execute_action(gesture):
            try:
                self.gesture_actions[gesture]()
                self.logger.info(f"Executed gesture action: {gesture}")
            except Exception as e:
                self.logger.error(f"Error executing gesture {gesture}: {e}")
    
    def execute_voice_command(self, command):
        """Execute action based on voice command"""
        if command in self.voice_actions and self.can_execute_action(command):
            try:
                self.voice_actions[command]()
                self.logger.info(f"Executed voice command: {command}")
            except Exception as e:
                self.logger.error(f"Error executing voice command {command}: {e}")
    
    # System Actions
    def open_browser(self):
        """Open web browser"""
        webbrowser.open('https://www.google.com')
    
    def close_browser(self):
        """Close current window"""
        pyautogui.hotkey('alt', 'f4')
    
    def volume_up(self):
        """Increase system volume"""
        pyautogui.press('volumeup')
    
    def volume_down(self):
        """Decrease system volume"""
        pyautogui.press('volumedown')
    
    def mute_audio(self):
        """Mute system audio"""
        pyautogui.press('volumemute')
    
    def unmute_audio(self):
        """Unmute system audio"""
        pyautogui.press('volumemute')
    
    def take_screenshot(self):
        """Take a screenshot"""
        screenshot = pyautogui.screenshot()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot.save(f"screenshot_{timestamp}.png")
    
    def open_calculator(self):
        """Open calculator application"""
        try:
            subprocess.run(['calc'], shell=True)
        except:
            # Alternative for Linux
            subprocess.run(['gnome-calculator'], shell=True)
    
    def open_notepad(self):
        """Open notepad/text editor"""
        try:
            subprocess.run(['notepad'], shell=True)
        except:
            # Alternative for Linux
            subprocess.run(['gedit'], shell=True)
    
    def minimize_window(self):
        """Minimize current window"""
        pyautogui.hotkey('win', 'down')
    
    def maximize_window(self):
        """Maximize current window"""
        pyautogui.hotkey('win', 'up')
    
    def switch_window(self):
        """Switch between open windows"""
        pyautogui.hotkey('alt', 'tab')
    
    def scroll_up(self):
        """Scroll up on current page"""
        pyautogui.scroll(3)
    
    def scroll_down(self):
        """Scroll down on current page"""
        pyautogui.scroll(-3)
    
    def zoom_in(self):
        """Zoom in"""
        pyautogui.hotkey('ctrl', 'plus')
    
    def zoom_out(self):
        """Zoom out"""
        pyautogui.hotkey('ctrl', 'minus')
    
    def mouse_click(self):
        """Perform mouse click at current position"""
        pyautogui.click()
    
    def close_application(self):
        """Close current application"""
        pyautogui.hotkey('alt', 'f4')
    
    def stop_action(self):
        """Stop current action (placeholder)"""
        pass
    
    def confirm_action(self):
        """Confirm action (Enter key)"""
        pyautogui.press('enter')
    
    def greeting(self):
        """Greeting response"""
        print("Hello! Gesture and voice system is ready.")
    
    def goodbye(self):
        """Goodbye response"""
        print("Goodbye! System shutting down.")