import cv2
import face_recognition
import json
import os
import time
import numpy as np

PROFILE_FILE = 'profiles.json'
FACES_DIR = 'faces'


def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'w') as f:
            json.dump({}, f)
    with open(PROFILE_FILE, 'r') as f:
        return json.load(f)


def save_profiles(profiles):
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)


def add_new_profile(name):
    profiles = load_profiles()
    key = name.lower().strip()

    # ensure faces directory exists
    os.makedirs(FACES_DIR, exist_ok=True)

    print(f"Capturing face for '{name}'. Please look at the camera.")
    cap = cv2.VideoCapture(0)
    time.sleep(2)

    start = time.time()
    face_detected_start = None
    face_detected_duration = 0
    while time.time() - start < 10:
        ret, frame = cap.read()
        if not ret:
            continue

        if isinstance(frame, np.ndarray):
            rgb_frame = frame
        else:
            rgb_frame = np.array(frame.convert("RGB"))

        # detect face locations
        face_locs = face_recognition.face_locations(rgb_frame)
        print(f"Debug: {len(face_locs)} face(s) detected")

        if face_locs:
            if face_detected_start is None:
                face_detected_start = time.time()
            face_detected_duration += time.time() - face_detected_start
            face_detected_start = time.time()

            if face_detected_duration >= 2.4:  # 80% of 3 seconds
                # save full-size frame into faces/ directory
                timestamp = int(time.time())
                filename = os.path.join(FACES_DIR, f"{key}_{timestamp}.jpg")
                cv2.imwrite(filename, frame)

                # record in profiles.json (optional: store a list of captures)
                profiles.setdefault(key, []).append(filename)
                save_profiles(profiles)

                print(f"✔ Face image saved to '{filename}'")
                break
        else:
            face_detected_start = None

        # draw boxes to help user align
        for top, right, bottom, left in face_locs:
            t, r, b, l = top*4, right*4, bottom*4, left*4
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)

        cv2.imshow('Capture Face - Press Q to cancel', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Capture canceled by user.")
            break
    else:
        print("Timeout: no face detected within 10 seconds.")

    cap.release()
    cv2.destroyAllWindows()


def verify_identity(name):
    profiles = load_profiles()
    key = name.lower().strip()
    if key not in profiles or not profiles[key]:
        print("Access denied: no such profile or no saved faces.")
        return False

    # use the most recent saved image for this profile
    fname = profiles[key][-1]
    if not os.path.exists(fname):
        print(f"Access denied: stored image '{fname}' missing.")
        return False

    print(f"Verifying '{name}'—look at the camera.")
    img = face_recognition.load_image_file(fname)
    known_locs = face_recognition.face_locations(img)
    known_encs = face_recognition.face_encodings(img, known_locs)
    if not known_encs:
        print("Error: couldn't extract encoding from stored image.")
        return False
    known = known_encs[0]

    cap = cv2.VideoCapture(0)
    time.sleep(2)
    start = time.time()
    while time.time() - start < 10:
        ret, frame = cap.read()
        if not ret:
            continue

        if isinstance(frame, np.ndarray):
            rgb_frame = frame
        else:
            rgb_frame = np.array(frame.convert("RGB"))

        locs = face_recognition.face_locations(rgb_frame)
        encs = face_recognition.face_encodings(rgb_frame, locs)
        print(f"Debug: {len(locs)} face(s), {len(encs)} encoding(s)")
        for e in encs:
            if face_recognition.compare_faces([known], e)[0]:
                print("✅ Access granted.")
                cap.release()
                cv2.destroyAllWindows()
                return True

        for top, right, bottom, left in locs:
            t, r, b, l = top*4, right*4, bottom*4, left*4
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)

        cv2.imshow('Verify Identity - Q to cancel', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("❌ Access denied: face not recognized.")
    cap.release()
    cv2.destroyAllWindows()
    return False


def main():
    while True:
        print("\n1. Add New Profile\n2. Verify Identity\n3. Exit")
        choice = input("Enter choice: ").strip()
        if choice == '1':
            add_new_profile(input("Name: "))
        elif choice == '2':
            verify_identity(input("Name: "))
        elif choice == '3':
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
