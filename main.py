import cv2
import mediapipe as mp
import time
import json
import numpy as np
import simpleaudio as sa

# === Load keys ===
with open('keys.json', 'r') as f:
    keys_hz = json.load(f)

# Sort notes from low to high
sorted_notes = sorted(keys_hz.items(), key=lambda x: x[1])
note_names = [note for note, hz in sorted_notes]
note_freqs = [hz for note, hz in sorted_notes]

# Settings
BASE_INDEX = 0  # Which note is "0 fingers" initially

# === Mediapipe setup ===
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

TIP_IDS = [4, 8, 12, 16, 20]

def count_fingers(lms, handedness):
    cnt = []
    if handedness == "Right":
        cnt.append(lms.landmark[TIP_IDS[0]].x < lms.landmark[TIP_IDS[0]-1].x)
    else:
        cnt.append(lms.landmark[TIP_IDS[0]].x > lms.landmark[TIP_IDS[0]-1].x)
    for i in range(1, 5):
        cnt.append(lms.landmark[TIP_IDS[i]].y < lms.landmark[TIP_IDS[i]-2].y)
    return sum(cnt)

def other_fingers_down(lms):
    for tip in (8, 12, 16, 20):
        if lms.landmark[tip].y < lms.landmark[tip-2].y:
            return False
    return True

# === Audio playing ===
def play_note(freq, duration=0.5):
    fs = 44100
    t = np.linspace(0, duration, int(fs * duration), False)
    wave = np.sin(freq * t * 2 * np.pi)
    audio = (wave * 32767).astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, fs)
    play_obj.wait_done()

# === Main loop ===
HOLD_TIME = 1.0
MOTION_THRESH = 0.5

prev_thumb_y = {"Left": None, "Right": None}
gesture_timer = {"Left": None, "Right": None}
mode = {"Left": None, "Right": None}

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    now = time.time()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    total = 0
    show_up = False
    show_down = False
    key_up = False
    key_down = False

    if res.multi_hand_landmarks and res.multi_handedness:
        for lms, meta in zip(res.multi_hand_landmarks, res.multi_handedness):
            hand = meta.classification[0].label
            total += count_fingers(lms, hand)

            tip = lms.landmark[4]
            base = lms.landmark[2]

            if other_fingers_down(lms):
                if tip.y < base.y:
                    cand = "up"
                elif tip.y > base.y:
                    cand = "down"
                else:
                    cand = None
            else:
                cand = None

            if cand:
                if mode[hand] is None:
                    if gesture_timer[hand] is None:
                        gesture_timer[hand] = now
                    elif now - gesture_timer[hand] >= HOLD_TIME:
                        mode[hand] = cand
            else:
                gesture_timer[hand] = None
                mode[hand] = None

            if mode[hand] == "up":
                show_up = True
            elif mode[hand] == "down":
                show_down = True

            prev_y = prev_thumb_y[hand]
            if mode[hand] and prev_y is not None:
                dy = prev_y - tip.y
                if mode[hand] == "up" and dy > MOTION_THRESH:
                    key_up = True
                if mode[hand] == "down" and dy < -MOTION_THRESH:
                    key_down = True

            prev_thumb_y[hand] = tip.y
            mp_drawing.draw_landmarks(frame, lms, mp_hands.HAND_CONNECTIONS)

    # === Handle playing ===
    # Note: Total fingers from all hands
    play_index = BASE_INDEX + total

    if 0 <= play_index < len(note_freqs):
        freq = note_freqs[play_index]
        cv2.putText(frame, f"Playing: {note_names[play_index]}", (10, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
        play_note(freq, 0.3)

    if key_up:
        BASE_INDEX += 1
        if BASE_INDEX > len(note_freqs) - 10:  # Keep room for fingers
            BASE_INDEX = len(note_freqs) - 10
    if key_down:
        BASE_INDEX -= 1
        if BASE_INDEX < 0:
            BASE_INDEX = 0

    cv2.putText(frame, f"Total Fingers: {total}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

    if show_up:
        cv2.putText(frame, "thumbup", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    elif show_down:
        cv2.putText(frame, "thumbdown", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    if key_up:
        cv2.putText(frame, "KeyUp", (10, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    elif key_down:
        cv2.putText(frame, "KeyDown", (10, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
