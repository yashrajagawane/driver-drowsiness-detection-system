import cv2
import dlib


def run_face_detection():
    # Open webcam
    cap = cv2.VideoCapture(0)

    # Improve camera resolution (optional but helpful)
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height

    # Load dlib face detector
    detector = dlib.get_frontal_face_detector()

    print("Starting face detection... Press 'q' to quit.")

    while True:
        success, frame = cap.read()

        if not success:
            print("Camera not working!")
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces (1 = upsample once for better accuracy)
        faces = detector(gray, 1)

        print("Faces detected:", len(faces))

        # Draw rectangles
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Show output
        cv2.imshow("Face Detection Test", frame)

        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()