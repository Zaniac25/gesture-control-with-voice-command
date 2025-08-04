"""
Configuration settings for the Hand Gesture Voice Control System
"""

# Camera Settings
CAMERA_INDEX = 0                # Default camera index (0 for built-in)
CAMERA_WIDTH = 1280             # Camera capture width
CAMERA_HEIGHT = 720             # Camera capture height
FPS = 30                        # Target frames per second

# MediaPipe Hands Settings
MIN_DETECTION_CONFIDENCE = 0.7  # Minimum confidence for hand detection
MIN_TRACKING_CONFIDENCE = 0.5   # Minimum confidence for hand tracking
MAX_NUM_HANDS = 2               # Maximum number of hands to detect

# Gesture Recognition Settings
GESTURE_THRESHOLD = 0.8         # Minimum confidence to accept a gesture
GESTURE_SMOOTHING = 5           # Number of frames for gesture smoothing buffer
GESTURE_HOLD_DURATION = 0.5     # Seconds to maintain gesture before executing

# Voice Command Settings
VOICE_TIMEOUT = 3               # Seconds to wait for voice command start
VOICE_PHRASE_TIME_LIMIT = 5     # Maximum duration of a voice command
MICROPHONE_INDEX = None         # None for default microphone
VOICE_SENSITIVITY = 0.5         # Microphone sensitivity (0-1)

# System Control Settings
ENABLE_SYSTEM_CONTROL = True    # Master switch for system control
ENABLE_VOICE_FEEDBACK = True    # Enable voice responses
ENABLE_GESTURE_CONTROL = True   # Enable gesture control
ENABLE_VOICE_CONTROL = True     # Enable voice control

# UI Settings
SHOW_LANDMARKS = True           # Display hand landmarks on camera feed
SHOW_GESTURE_INFO = True        # Display recognized gesture info
SHOW_VOICE_STATUS = True        # Display voice command status
UI_FONT_SIZE = 0.7              # On-screen display font size
UI_FONT_COLOR = (0, 255, 0)    # BGR color for UI text

# Application Behavior
ACTION_COOLDOWN = 1.0           # Seconds between allowed actions
AUTO_SAVE_INTERVAL = 300        # Seconds between auto-saves (0 to disable)

# Path Configuration
MODEL_PATH = 'models/gesture_classifier.pkl'
TRAINING_DATA_PATH = 'models/training_data/'
COMMANDS_CONFIG_PATH = 'config/commands.json'
LOG_FILE_PATH = 'logs/system.log'

# Debug Settings
DEBUG_MODE = False              # Enable debug outputs
LOG_LEVEL = 'INFO'              # DEBUG, INFO, WARNING, ERROR, CRITICAL
SAVE_FRAMES = False             # Save processed frames for debugging
FRAME_SAVE_PATH = 'debug_frames/'

# Gesture to Action Mapping (Can be overridden in commands.json)
DEFAULT_GESTURE_MAPPINGS = {
    'fist': 'close_application',
    'palm': 'stop_action',
    'thumbs_up': 'volume_up',
    'peace': 'screenshot',
    'ok': 'confirm_action',
    'point': 'mouse_click'
}

# Voice Command Mappings (Can be extended in commands.json)
DEFAULT_VOICE_COMMANDS = {
    'open browser': 'open_browser',
    'close browser': 'close_browser',
    'volume up': 'volume_up',
    'volume down': 'volume_down',
    'mute': 'mute_audio',
    'unmute': 'unmute_audio',
    'take screenshot': 'screenshot',
    'open calculator': 'open_calculator'
}

def validate_settings():
    """Validate and correct settings if needed"""
    # Ensure paths exist
    import os
    os.makedirs(TRAINING_DATA_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    
    # Clamp values to valid ranges
    global MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE
    MIN_DETECTION_CONFIDENCE = max(0.0, min(1.0, MIN_DETECTION_CONFIDENCE))
    MIN_TRACKING_CONFIDENCE = max(0.0, min(1.0, MIN_TRACKING_CONFIDENCE))
    
    # Verify camera can be opened
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            raise ValueError(f"Camera index {CAMERA_INDEX} not available")
        cap.release()
    except:
        pass

# Run validation when module loads
validate_settings()