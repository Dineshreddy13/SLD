# SignDetect

SignDetect is a real-time, AI-powered Sign Language translation dashboard. It leverages a custom machine learning pipeline (MediaPipe + TensorFlow Lite) on a Python/FastAPI backend to detect hand landmarks from live video, classifying gestures into American Sign Language letters and numbers, and streaming the results via WebSocket to a responsive, modern React frontend.

## Features
- **Real-Time Translation**: Classifies static ASL signs instantly using a sliding-window temporal smoothing algorithm.
- **Sentence Builder**: Accumulate confirmed signs into full sentences with space and delete controls.
- **Text-to-Speech (TTS)**: Speak out your translated sentences aloud using Google TTS.
- **Session History**: Easily browse, replay, and manage your past sentences.
- **Accessible & Responsive**: Fully keyboard navigable, mindful of `prefers-reduced-motion`, and beautifully designed for both desktop and mobile.

## Known Limitations
* **Dynamic Signs Excluded**: ASL letters **J** and **Z** are motion-based signs that require spatiotemporal tracking. They are explicitly excluded from Version 1 of this project, which focuses strictly on feedforward classification of static poses. 

---

## Setup & Running Locally

### 1. Start the Backend
The backend runs on Python and requires a virtual environment.
```bash
cd backend
# Create a venv if you haven't (requires Python 3.14 for the main app)
# Activate the venv and install requirements
pip install -r requirements.txt

# Run the FastAPI server (must be bound to 127.0.0.1 for WebSocket CORS)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Start the Frontend
The frontend is a Vite + React + Zustand application.
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (or the port Vite provides) in your browser. Grant camera permissions when prompted, and start signing!
