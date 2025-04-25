import cv2
import mediapipe as mp
import time

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
                if mode[hand] == "up" and dy > MOTION_THRESH: key_up = True
                if mode[hand] == "down" and dy < -MOTION_THRESH: key_down = True

            prev_thumb_y[hand] = tip.y
            mp_drawing.draw_landmarks(frame, lms, mp_hands.HAND_CONNECTIONS)

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
