import cv2
import dlib
import winsound
import imutils
import time
from src.ear import eye_aspect_ratio


EAR_THRESHOLD = 0.25
DROWSY_SECONDS = 1.1


# -----------------------------
# System State (Dashboard Data)
# -----------------------------
system_state = {
    "ear": 0,
    "faces": 0,
    "status": "Initializing...",
    "fatigue": 0
}


# -----------------------------
# Alarm Controls
# -----------------------------
def sound_alarm():
    winsound.PlaySound(
        "sounds/alarm.wav",
        winsound.SND_ASYNC | winsound.SND_LOOP
    )


def stop_alarm():
    winsound.PlaySound(None, winsound.SND_PURGE)


# -----------------------------
# Frame Generator (Flask Stream)
# -----------------------------
def generate_frames():

    cap = cv2.VideoCapture(0)

    # Reduce camera buffering (prevents lag)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("[ERROR] Could not open camera")
        return

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(
        "models/shape_predictor_68_face_landmarks.dat"
    )

    print("[INFO] Starting AI Driver Monitoring System")

    eyes_closed_start = None
    alarm_on = False

    # FPS tracking
    prev_time = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        # Resize for performance
        frame = imutils.resize(frame, width=480)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray, 0)

        system_state["faces"] = len(faces)

        cv2.putText(
            frame,
            f"Faces: {len(faces)}",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

        if len(faces) == 0:
            eyes_closed_start = None
            system_state["status"] = "No Face Detected"

        # Process only the first detected face (prevents lag)
        for face in faces[:1]:

            x1 = max(0, face.left())
            y1 = max(0, face.top())
            x2 = min(frame.shape[1], face.right())
            y2 = min(frame.shape[0], face.bottom())

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)

            left_eye = []
            right_eye = []

            for n in range(36, 42):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                left_eye.append((x, y))

            for n in range(42, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                right_eye.append((x, y))

            # Calculate EAR
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            ear = (left_ear + right_ear) / 2.0

            system_state["ear"] = round(ear, 2)

            fatigue = int((1 - ear) * 100)
            fatigue = max(0, min(fatigue, 100))

            system_state["fatigue"] = fatigue

            cv2.putText(
                frame,
                f"EAR: {ear:.2f}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

            # -----------------------------
            # Drowsiness Detection
            # -----------------------------
            if ear < EAR_THRESHOLD:

                if eyes_closed_start is None:
                    eyes_closed_start = time.time()

                time_closed = time.time() - eyes_closed_start

                system_state["status"] = "Eyes Closing..."

                if time_closed >= DROWSY_SECONDS:

                    system_state["status"] = "DROWSY!"

                    if not alarm_on:
                        alarm_on = True
                        sound_alarm()

                    cv2.putText(
                        frame,
                        "DROWSINESS ALERT!",
                        (110, 200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.1,
                        (0, 0, 255),
                        4
                    )

            else:

                eyes_closed_start = None
                system_state["status"] = "Awake"

                if alarm_on:
                    alarm_on = False
                    stop_alarm()

        # -----------------------------
        # FPS Counter (Performance)
        # -----------------------------
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time else 0
        prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        # Encode frame for browser streaming
        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

    cap.release()
    stop_alarm()