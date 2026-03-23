# 🚗 AI Driver Drowsiness Detection System

A **real-time AI-powered driver monitoring system** that detects driver fatigue using computer vision and alerts the user to prevent accidents.

This project uses **Flask, OpenCV, and Dlib** to analyze eye movements from a live browser camera feed and detect drowsiness using the **Eye Aspect Ratio (EAR)** algorithm.

---

## 🌐 Live Demo

[![Launch Demo](https://img.shields.io/badge/🚗%20Open%20Live%20Dashboard-Click%20Here-success?style=for-the-badge)](https://smart-driver-monitor.onrender.com)

> ⚠️ Note: Free Render server may take **30–50 seconds** to start on first request.

---

## 🚀 Key Features

* 🚗 Real-time driver monitoring
* 👁️ Eye Aspect Ratio (EAR) based fatigue detection
* 📷 Live browser camera integration (WebRTC)
* 🚨 Automatic alert system for drowsiness
* ⚡ Real-time dashboard updates
* 🎨 Clean and modern UI
* ☁️ Cloud deployment using Render
* 🔄 Continuous frame processing via Flask API

---

## 🧠 How It Works

1. Captures frames from the browser camera
2. Sends frames to Flask backend
3. Detects face using Dlib facial landmarks
4. Calculates Eye Aspect Ratio (EAR)
5. Compares EAR with threshold values
6. Detects drowsiness and triggers alert
7. Updates live dashboard

---

## 📊 Drowsiness Detection Formula

```
EAR = (||p2 − p6|| + ||p3 − p5||) / (2 ||p1 − p4||)
```

### Detection Logic

| Condition                            | Result           |
| ------------------------------------ | ---------------- |
| EAR above threshold                  | Driver Awake     |
| EAR below threshold (short duration) | Eye Blink        |
| EAR below threshold (long duration)  | Drowsiness Alert |

---

## 🏗️ Project Structure

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

## ⚙️ Tech Stack

* Python
* Flask
* OpenCV
* Dlib
* NumPy
* JavaScript
* HTML / CSS
* Render (Deployment)

---

## 🚀 Installation & Setup

### Clone the repository

```bash
git clone https://github.com/yashrajagawane/driver-drowsiness-detection-system.git
cd driver-drowsiness-detection-system
```

### Create virtual environment

```bash
python -m venv venv
```

### Activate environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

### Open in browser

```
http://127.0.0.1:5000
```

---

## ☁️ Deployment

This project is deployed using **Render Cloud Platform**.

### Steps:

1. Push code to GitHub
2. Create Web Service on Render
3. Connect your repository
4. Set build command:

```bash
pip install -r requirements.txt
```

5. Set start command:

```bash
gunicorn app:app
```

---

## 🎯 Use Cases

* 🚗 Driver safety systems
* 🚛 Fleet management monitoring
* 🤖 AI-based fatigue detection
* 🚘 Smart vehicle applications

---

## 🔮 Future Improvements

* Head pose detection
* Blink rate analysis
* Deep learning-based fatigue detection
* Mobile device optimization
* Multi-driver detection

---

## 👨‍💻 Author

**Yashraj Agawane**

🔗 GitHub: https://github.com/yashrajagawane

---

## ⭐ Support

If you found this project helpful, please give it a **star ⭐ on GitHub** — it motivates further development!

---
