🖐️🎙️ Hand Gesture & Voice Control System

A powerful Python-based system that allows users to control their computer using hand gestures and voice commands — enabling touchless human-computer interaction.

This project uses Computer Vision and Speech Recognition to perform system-level operations like cursor control, clicking, scrolling, volume adjustment, screenshots, and more.

🚀 Features
🖐️ Gesture Controls

Cursor movement using index finger tracking:

Left click / Right click
Double click
Scroll up / Scroll down
Volume control
Screenshot capture
System lock
Smooth cursor movement using EMA (Exponential Moving Average)
Cooldown protection to prevent repeated triggers

🎙️ Voice Controls:

Wake word: "computer"
Short activation window after wake word

Commands like:

Open applications
Volume up/down
Take screenshot
Lock system
Shutdown (optional)
Thread-based voice listener for non-blocking performance

🛡️ Safety Features

PyAutoGUI failsafe
Action cooldown timers
Camera warm-up handling
Rotating logs for debugging
Configurable gesture-action mapping
Adjustable sensitivity & smoothing

🏗️ Project Structure
hand_gesture_voice_system/
│
├── main.py
├── modules/
│   ├── gesture_recognition.py
│   ├── voice_commands.py
│   ├── system_controller.py
│   └── utils.py
│
├── models/
│   ├── gesture_classifier.pkl
│   └── training_data/
│
├── config/
│   ├── settings.py
│   └── commands.json
│
├── requirements.txt
├── examples/
│   └── basic_demo.py
├── docs/
│   └── setup_guide.md

🧠Technologies Used 

Python
OpenCV
MediaPipe
PyAutoGUI
SpeechRecognition
Threading
JSON Configuration
Logging (RotatingFileHandler)

⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/yourusername/hand-gesture-voice-control.git
cd hand-gesture-voice-control

2️⃣ Create Virtual Environment (Recommended)
python -m venv venv


Activate it:

Windows
venv\Scripts\activate


Mac/Linux
source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

▶️ How to Run
python main.py


Make sure:

Your webcam is connected
Microphone is enabled
Proper permissions are granted

🎯 Gesture Mapping (Example)
Gesture	Action
1 Finger	Move Cursor
2 Fingers	Left Click
3 Fingers	Right Click
Pinch	Drag
Palm Open	Scroll
Fist	Lock System
(Mappings can be modified in commands.json)

🎙️ Voice Command Flow

Say "computer"
System activates listening window
Speak command within activation time

Example:

computer open chrome
computer volume up
computer take screenshot

🔧 Configuration

All customizable parameters are inside:

config/settings.py
config/commands.json


You can modify:

Cursor sensitivity
Smoothing factor
Cooldown time
Wake word
Gesture-to-action mapping
Voice commands

📊 System Architecture

Camera captures frames
MediaPipe detects hand landmarks
Gesture recognition logic processes landmarks
Action mapped to system_controller
Voice thread listens for wake word
Recognized command triggers system action
Both gesture and voice modules run efficiently without blocking the main loop.

🛠️ Future Improvements

Multi-hand recognition
Custom gesture training UI
GUI dashboard
Cross-platform optimization
AI-based dynamic gesture learning
Integration with IoT devices

📸 Demo (Add Screenshots Here)

You can add:
Running application screenshot
Hand landmark detection
HUD display
Voice activation message

📌 Use Cases

Accessibility support
Touchless interaction
Smart classrooms
Presentations
Automation enthusiasts
Smart home integration

🧪 Requirements

Python 3.8+
Webcam
Microphone
Windows/Linux/Mac

👨‍💻 Author

zaniac25
B.Tech CSE | AI/ML Enthusiast | Computer Vision Developer

⭐ If You Like This Project
Give it a ⭐ on GitHub and feel free to contribute!