from flask import Flask, render_template, redirect, url_for
import threading
from src.face_detector import run_face_detection

# Initialize Flask app
app = Flask(__name__)

# Flag to track if detection is already running
detection_running = False


# -------------------------------
# Home Page Route
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------
# Start Detection Route
# -------------------------------
@app.route("/start_detection", methods=["POST"])
def start_detection():

    global detection_running

    if not detection_running:
        print("[INFO] Starting Driver Drowsiness Detection System...")

        detection_running = True

        # Run detection in a separate thread
        thread = threading.Thread(target=run_detection_thread)
        thread.daemon = True
        thread.start()

    else:
        print("[INFO] Detection already running.")

    return redirect(url_for("index"))


# -------------------------------
# Thread Function
# -------------------------------
def run_detection_thread():
    global detection_running

    try:
        run_face_detection()
    finally:
        detection_running = False
        print("[INFO] Detection stopped.")


# -------------------------------
# Run Flask Server
# -------------------------------
if __name__ == "__main__":
    print("\n[INFO] Flask server started.")
    print("[INFO] Open browser → http://127.0.0.1:5000\n")

    app.run(debug=True)