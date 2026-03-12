from flask import Flask, render_template, Response, jsonify
from src.face_detector import generate_frames, system_state

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/metrics')
def metrics():
    return jsonify(system_state)

if __name__ == '__main__':
    print("\n==============================")
    print(" AI DRIVER MONITORING SYSTEM ")
    print("==============================\n")
    print("Open browser → http://127.0.0.1:5000\n")

    app.run(debug=True, threaded=True, use_reloader=False)