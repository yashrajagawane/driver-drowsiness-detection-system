#🚗 AI Driver Drowsiness Detection System

A real-time AI driver monitoring system that detects fatigue using Eye Aspect Ratio (EAR) and computer vision. 
It analyzes eye movements through the browser camera and triggers alerts when drowsiness is detected.

Built using Python, Flask, OpenCV, and Dlib for efficient real-time facial landmark detection and monitoring.

---

## 🌐 Live Demo

Experience the **AI Driver Monitoring Dashboard** in real-time.

[![Launch Demo](https://img.shields.io/badge/🚗%20Open%20Live%20Dashboard-Click%20Here-success?style=for-the-badge)](https://smart-driver-monitor.onrender.com)

> ⚠️ The free Render server may take **30–50 seconds to wake up** on first request.
---

## 🧠 Features

* 🚗 **Real-time driver monitoring**
* 👁️ **Eye Aspect Ratio (EAR) based fatigue detection**
* 📷 **Browser camera access using WebRTC**
* ⚡ **Live telemetry dashboard**
* 🚨 **Automatic alarm when driver is drowsy**
* 🎨 **Tesla-inspired dark UI dashboard**
* 🌐 **Cloud deployment using Render**
* 🔄 **Continuous frame processing using Flask API**

---

## 🖥️ System Architecture

```
Browser Camera
      │
      ▼
JavaScript Frame Capture
      │
      ▼
Send Frames (AJAX / Fetch API)
      │
      ▼
Flask Backend API
      │
      ▼
OpenCV + Dlib Face Landmark Detection
      │
      ▼
Eye Aspect Ratio Calculation
      │
      ▼
Drowsiness Detection
      │
      ▼
Live Dashboard Update + Alarm
```

---

## 📂 Project Structure

```
driver-drowsiness-detection-system
│
├── app.py
├── requirements.txt
├── Procfile
├── .python-version
│
├── models/
│   └── shape_predictor_68_face_landmarks.dat
│
├── src/
│   └── ear.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── alarm.wav
│
└── README.md
```

---

## ⚙️ Technologies Used

* Python
* Flask
* OpenCV
* Dlib
* NumPy
* JavaScript
* HTML / CSS
* Render (Cloud Deployment)

---

## 📊 Drowsiness Detection Algorithm

The system uses **Eye Aspect Ratio (EAR)** to detect fatigue.

```
EAR = (||p2 − p6|| + ||p3 − p5||) / (2 ||p1 − p4||)
```

Where the eye landmarks are obtained using the **68-point facial landmark model**.

### Detection Logic

| Condition                               | System Response  |
| --------------------------------------- | ---------------- |
| EAR above threshold                     | Driver Awake     |
| EAR below threshold briefly             | Eyes Closing     |
| EAR below threshold for longer duration | Drowsiness Alert |

---

## 🚀 Installation (Local Setup)

Clone the repository:

```bash
git clone https://github.com/yashrajagawane/driver-drowsiness-detection-system.git
cd driver-drowsiness-detection-system
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## ☁️ Deployment

This project is deployed using **Render Cloud Platform**.

Steps used for deployment:

1. Push project to GitHub
2. Create Web Service on Render
3. Connect GitHub repository
4. Set build command

```
pip install -r requirements.txt
```

5. Set start command

```
gunicorn app:app
```

---

## 🎯 Use Cases

* Driver monitoring systems
* Automotive safety applications
* Fleet management systems
* Smart vehicle safety AI
* Real-time fatigue detection

---

## 📸 Screenshots

*(You can add screenshots of your dashboard here)*

---

## 🔮 Future Improvements

* Head pose detection
* Blink rate monitoring
* Face bounding box visualization
* Mobile device optimization
* Deep learning based fatigue detection
* Multi-driver detection support

---

## 👨‍💻 Author

**Yashraj Agawane**

GitHub
https://github.com/yashrajagawane

---

## ⭐ Support

If you found this project useful, consider giving it a **star ⭐ on GitHub**.
