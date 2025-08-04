# Hand Gesture Voice Control System

![System Demo](docs/assets/system_architecture.png)

A Python-based system for controlling computer functions using hand gestures and voice commands, combining computer vision and speech recognition technologies.

## Features

- ✋ **Gesture Recognition**: Real-time hand tracking with MediaPipe
- 🎤 **Voice Commands**: Natural language processing with speech recognition
- 🖥️ **System Control**: Volume, applications, browser, and OS controls
- 🧠 **Machine Learning**: Custom gesture training with RandomForest
- ⚡ **Multi-threaded**: Simultaneous gesture and voice processing
- 📊 **Performance Monitoring**: Real-time FPS and accuracy tracking

## System Architecture

```mermaid
graph TD
    A[Camera] --> B[Gesture Recognition]
    C[Microphone] --> D[Voice Processing]
    B --> E[System Controller]
    D --> E
    E --> F[Volume Control]
    E --> G[Application Control]
    E --> H[Window Management]