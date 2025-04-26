# Project Overview

This project is a multi-functional application that combines face recognition, hand gesture-based music playing, and Arduino-based sound output. It is designed to interact with users through a camera and an Arduino device, providing a unique experience of music and security.

## Components

### 1. Face Recognition (`faceReco.py`)
- **Purpose**: To add and verify user profiles using face recognition.
- **Key Functions**:
  - `add_new_profile(name)`: Captures and saves a user's face image to create a new profile.
  - `verify_identity(name)`: Verifies a user's identity by comparing the live camera feed with stored face images.

### 2. Hand Gesture Music Player (`main.py`)
- **Purpose**: To play musical notes based on hand gestures detected via a webcam.
- **Key Features**:
  - Uses MediaPipe to detect hand landmarks.
  - Plays notes based on the number of fingers detected.
  - Allows changing the base note using thumb gestures.

### 3. Arduino Speaker (`arduino.py`)
- **Purpose**: To play music notes through an Arduino-connected speaker.
- **Key Functions**:
  - `play_music_sheet(music_sheet)`: Sends frequency data to the Arduino to play music.

### 4. Sound Playback (`playsound.py`)
- **Purpose**: To play sound files using the `pydub` and `simpleaudio` libraries.
- **Key Functions**:
  - `playsound(music_file)`: Plays an MP3 file.

## Data Files

### 1. Profiles (`profiles.json`)
- **Purpose**: Stores user profiles with associated face image paths.
- **Structure**: JSON object with user names as keys and lists of image paths as values.

### 2. Musical Notes (`keys.json`)
- **Purpose**: Maps musical note names to their corresponding frequencies.
- **Structure**: JSON object with note names as keys and frequencies as values.

## Setup and Usage

1. **Environment Setup**:
   - Ensure Python is installed.
   - Install required libraries: `opencv-python`, `face_recognition`, `mediapipe`, `pydub`, `simpleaudio`, `pyserial`.

2. **Running the Application**:
   - **Face Recognition**: Run `faceReco.py` to add or verify profiles.
   - **Hand Gesture Music Player**: Run `main.py` to start the hand gesture-based music player.
   - **Arduino Speaker**: Use `arduino.py` to play music through an Arduino device.

3. **Configuration**:
   - Update `profiles.json` and `keys.json` as needed to manage profiles and musical notes.

## Notes

- Ensure your camera is properly connected for face recognition and hand gesture detection.
- For Arduino functionality, ensure the device is connected to the correct port.
- The `faces/` directory is used to store captured face images and is ignored by version control as specified in `.gitignore`.

## TODO

- [ ] Implement a function to delete a user profile from `profiles.json`.
- [ ] Document the `add_new_profile` function with detailed usage instructions.
- [ ] Optimize the face detection loop for better performance.
- [ ] Consider adding a GUI for easier interaction with the face recognition system.
- [ ] Pack to executable program
