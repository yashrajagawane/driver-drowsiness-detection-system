import cv2
import dlib
import os


def run_face_detection():
    # Open webcam
    cap = cv2.VideoCapture(0)

    # Improve camera resolution
    cap.set(3, 640)
    cap.set(4, 480)

    # Load dlib face detector
    detector = dlib.get_frontal_face_detector()

    # Model path
    model_path = "models/shape_predictor_68_face_landmarks.dat"

    # Check if model exists
    if not os.path.exists(model_path):
        print("Model file not found! Run download_model.py first.")
        return

    predictor = dlib.shape_predictor(model_path)

    print("Starting face & eye detection... Press 'q' to quit.")

    while True:
        success, frame = cap.read()

        if not success:
            print("Camera not working!")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray, 1)

        # Display face count
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        for face in faces:
            # Safe bounding box
            x1 = max(0, face.left())
            y1 = max(0, face.top())
            x2 = min(frame.shape[1], face.right())
            y2 = min(frame.shape[0], face.bottom())

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)

            # Draw eye landmarks (36-47)
            for n in range(36, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

        cv2.imshow("Face and Eye Detection Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()