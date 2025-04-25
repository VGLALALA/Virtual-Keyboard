import serial
import time

PORT = "COM3"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("Connected to Arduino!")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Arduino says: {line}")
except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
