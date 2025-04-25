import serial
import time

class ArduinoSpeaker:
    def __init__(self, port, baudrate=9600):
        print(f"Connecting to Arduino on {port}...")
        self.arduino = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2)  # Wait for Arduino reset

    def play_music_sheet(self, music_sheet):
        for hz in music_sheet:
            if hz == 0:
                self.arduino.write(b'0\n')  # Convention: 0 for pause
            else:
                self.arduino.write(f"{hz}\n".encode())
            time.sleep(0.5)  # Wait between notes

    def close(self):
        self.arduino.close()
