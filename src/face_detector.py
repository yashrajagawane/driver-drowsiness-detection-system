import cv2
import dlib
import os
from src.ear import eye_aspect_ratio


# --- Detection Settings ---
EAR_THRESHOLD = 0.25        # If EAR is below this, eyes are considered closed
CONSECUTIVE_FRAMES = 20     # Frames eyes must stay closed before triggering alert
# ---------------------------


def run_face_detection():

    # Check if landmark model exists
    model_path = "models/shape_predictor_68_face_landmarks.dat"
    if not os.path.exists(model_path):
        print("Model file not found! Please run download_model.py first.")
        return

    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # Load dlib detectors
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)

    print("Starting Driver Drowsiness Detection... Press 'q' to quit.")

    frame_counter = 0

    while True:

        success, frame = cap.read()

        if not success:
            print("Camera not working!")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray, 1)

        # Show number of detected faces
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

            # Extract left eye
            left_eye = []
            for n in range(36, 42):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                left_eye.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            # Extract right eye
            right_eye = []
            for n in range(42, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                right_eye.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            # Calculate EAR
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            ear = (left_ear + right_ear) / 2.0

            # Display EAR
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # --- Drowsiness Detection Logic ---
            if ear < EAR_THRESHOLD:

                frame_counter += 1

                if frame_counter >= CONSECUTIVE_FRAMES:

                    cv2.putText(frame,
                                "DROWSINESS ALERT!",
                                (100, 200),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.5,
                                (0, 0, 255),
                                4)

            else:
                frame_counter = 0
            # -----------------------------------

        cv2.imshow("Driver Drowsiness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()