import cv2
import dlib
import os
import winsound
from src.ear import eye_aspect_ratio

# --- Detection Settings ---
EAR_THRESHOLD = 0.25
CONSECUTIVE_FRAMES = 15
# ---------------------------


def sound_alarm():
    """Play alarm sound asynchronously"""
    winsound.PlaySound("sounds/alarm.wav", winsound.SND_ASYNC)


def run_face_detection():

    model_path = "models/shape_predictor_68_face_landmarks.dat"
    alarm_path = "sounds/alarm.wav"

    # Check required files
    if not os.path.exists(model_path):
        print("Face landmark model not found! Run download_model.py first.")
        return

    if not os.path.exists(alarm_path):
        print("Alarm sound file not found in sounds/ folder.")
        return

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)

    print("Driver Drowsiness Detection Started... Press 'q' to quit.")

    frame_counter = 0
    alarm_on = False

    while True:

        success, frame = cap.read()

        if not success:
            print("Camera not working!")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray, 1)

        # Display number of faces detected
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if len(faces) == 0:
            frame_counter = 0

        for face in faces:

            # Safe bounding box
            x1 = max(0, face.left())
            y1 = max(0, face.top())
            x2 = min(frame.shape[1], face.right())
            y2 = min(frame.shape[0], face.bottom())

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)

            left_eye = []
            right_eye = []

            # Left eye landmarks (36–41)
            for n in range(36, 42):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                left_eye.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            # Right eye landmarks (42–47)
            for n in range(42, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                right_eye.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            # Calculate EAR
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            ear = (left_ear + right_ear) / 2.0

            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # ---- Drowsiness Detection ----
            if ear < EAR_THRESHOLD:

                frame_counter += 1

                if frame_counter >= CONSECUTIVE_FRAMES:

                    if not alarm_on:
                        alarm_on = True
                        sound_alarm()

                    cv2.putText(frame,
                                "DROWSINESS ALERT!",
                                (100, 200),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.2,
                                (0, 0, 255),
                                4)

            else:
                frame_counter = 0
                alarm_on = False
            # --------------------------------

        cv2.imshow("Driver Drowsiness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()