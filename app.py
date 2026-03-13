from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import dlib
import time
import os
from src.ear import eye_aspect_ratio

app = Flask(__name__)

# -----------------------------
# SETTINGS
# -----------------------------
EAR_THRESHOLD = 0.25
DROWSY_SECONDS = 1.1
FRAME_WIDTH = 450  # resize for faster detection

# -----------------------------
# LOAD MODELS
# -----------------------------
print("[INFO] Loading facial landmark model...")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "models/shape_predictor_68_face_landmarks.dat"
)

print("[INFO] Model loaded successfully")

# -----------------------------
# GLOBAL STATE
# -----------------------------
eyes_closed_start = None


# -----------------------------
# HELPER: Decode Base64 Image
# -----------------------------
def decode_image(base64_string):

    try:

        encoded_data = base64_string.split(",")[1]

        img_bytes = base64.b64decode(encoded_data)

        np_arr = np.frombuffer(img_bytes, np.uint8)

        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return frame

    except Exception as e:

        print("[ERROR] Image decoding failed:", e)

        return None


# -----------------------------
# HELPER: Run AI Detection
# -----------------------------
def detect_drowsiness(frame):

    global eyes_closed_start

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray, 0)

    status = "SYSTEM ACTIVE"
    ear_value = 0.0
    fatigue = 0
    is_drowsy = False
    is_closing = False

    if len(faces) == 0:

        eyes_closed_start = None
        status = "SCANNING FOR DRIVER..."

        return status, ear_value, fatigue, is_drowsy, is_closing, faces

    for face in faces:

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

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        ear = (left_ear + right_ear) / 2.0

        ear_value = round(ear, 2)

        fatigue = max(0, min(int((1 - ear) * 100), 100))

        # -----------------------------
        # DROWSINESS LOGIC
        # -----------------------------
        if ear < EAR_THRESHOLD:

            if eyes_closed_start is None:
                eyes_closed_start = time.time()

            closed_time = time.time() - eyes_closed_start

            status = "EYES CLOSING..."
            is_closing = True

            fatigue = min(100, int((closed_time / DROWSY_SECONDS) * 100))

            if closed_time >= DROWSY_SECONDS:

                status = "⚠ CRITICAL: DROWSY!"
                is_drowsy = True
                is_closing = False

        else:

            eyes_closed_start = None

            status = "AWAKE"

    return status, ear_value, fatigue, is_drowsy, is_closing, faces


# -----------------------------
# ROUTE: Dashboard
# -----------------------------
@app.route("/")
def index():

    return render_template("index.html")


# -----------------------------
# ROUTE: AI Detection API
# -----------------------------
@app.route("/detect", methods=["POST"])
def detect():

    try:

        data = request.get_json()

        if not data or "image" not in data:

            return jsonify({"error": "No image received"}), 400

        frame = decode_image(data["image"])

        if frame is None:

            return jsonify({"error": "Invalid image"}), 400

        # Resize frame for faster processing
        height, width = frame.shape[:2]

        if width > FRAME_WIDTH:

            ratio = FRAME_WIDTH / width
            frame = cv2.resize(
                frame,
                (FRAME_WIDTH, int(height * ratio))
            )

        # Run AI detection
        status, ear_value, fatigue, is_drowsy, is_closing, faces = detect_drowsiness(frame)

        return jsonify({
            "status": status,
            "ear": ear_value,
            "faces": len(faces),
            "fatigue": fatigue,
            "is_drowsy": is_drowsy,
            "is_closing": is_closing
        })

    except Exception as e:

        print("[ERROR]", e)

        return jsonify({"error": str(e)}), 500


# -----------------------------
# START SERVER
# -----------------------------
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import dlib
import time
import os
from src.ear import eye_aspect_ratio

app = Flask(__name__)

# -----------------------------
# SETTINGS
# -----------------------------
EAR_THRESHOLD = 0.25
DROWSY_SECONDS = 1.1
FRAME_WIDTH = 450  # resize for faster detection

# -----------------------------
# LOAD MODELS
# -----------------------------
print("[INFO] Loading facial landmark model...")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "models/shape_predictor_68_face_landmarks.dat"
)

print("[INFO] Model loaded successfully")

# -----------------------------
# GLOBAL STATE
# -----------------------------
eyes_closed_start = None


# -----------------------------
# HELPER: Decode Base64 Image
# -----------------------------
def decode_image(base64_string):

    try:

        encoded_data = base64_string.split(",")[1]

        img_bytes = base64.b64decode(encoded_data)

        np_arr = np.frombuffer(img_bytes, np.uint8)

        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return frame

    except Exception as e:

        print("[ERROR] Image decoding failed:", e)

        return None


# -----------------------------
# HELPER: Run AI Detection
# -----------------------------
def detect_drowsiness(frame):

    global eyes_closed_start

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray, 0)

    status = "SYSTEM ACTIVE"
    ear_value = 0.0
    fatigue = 0
    is_drowsy = False
    is_closing = False

    if len(faces) == 0:

        eyes_closed_start = None
        status = "SCANNING FOR DRIVER..."

        return status, ear_value, fatigue, is_drowsy, is_closing, faces

    for face in faces:

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

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        ear = (left_ear + right_ear) / 2.0

        ear_value = round(ear, 2)

        fatigue = max(0, min(int((1 - ear) * 100), 100))

        # -----------------------------
        # DROWSINESS LOGIC
        # -----------------------------
        if ear < EAR_THRESHOLD:

            if eyes_closed_start is None:
                eyes_closed_start = time.time()

            closed_time = time.time() - eyes_closed_start

            status = "EYES CLOSING..."
            is_closing = True

            fatigue = min(100, int((closed_time / DROWSY_SECONDS) * 100))

            if closed_time >= DROWSY_SECONDS:

                status = "⚠ CRITICAL: DROWSY!"
                is_drowsy = True
                is_closing = False

        else:

            eyes_closed_start = None

            status = "AWAKE"

    return status, ear_value, fatigue, is_drowsy, is_closing, faces


# -----------------------------
# ROUTE: Dashboard
# -----------------------------
@app.route("/")
def index():

    return render_template("index.html")


# -----------------------------
# ROUTE: AI Detection API
# -----------------------------
@app.route("/detect", methods=["POST"])
def detect():

    try:

        data = request.get_json()

        if not data or "image" not in data:

            return jsonify({"error": "No image received"}), 400

        frame = decode_image(data["image"])

        if frame is None:

            return jsonify({"error": "Invalid image"}), 400

        # Resize frame for faster processing
        height, width = frame.shape[:2]

        if width > FRAME_WIDTH:

            ratio = FRAME_WIDTH / width
            frame = cv2.resize(
                frame,
                (FRAME_WIDTH, int(height * ratio))
            )

        # Run AI detection
        status, ear_value, fatigue, is_drowsy, is_closing, faces = detect_drowsiness(frame)

        return jsonify({
            "status": status,
            "ear": ear_value,
            "faces": len(faces),
            "fatigue": fatigue,
            "is_drowsy": is_drowsy,
            "is_closing": is_closing
        })

    except Exception as e:

        print("[ERROR]", e)

        return jsonify({"error": str(e)}), 500


# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    print(f"[INFO] Starting server on port {port}")

    app.run(host="0.0.0.0", port=5000)