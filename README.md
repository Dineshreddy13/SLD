# SignDetect (SLD)

![SignDetect](https://raw.githubusercontent.com/Dineshreddy13/SLD/master/frontend/public/logo.png)

Real-time, AI-powered American Sign Language (ASL) translation dashboard — a full-stack demo combining a Python/FastAPI backend (MediaPipe + ML inference) with a Vite + React frontend and lightweight TTS.

---

## Table of contents
- About
- Features
- Tech stack
- Repo layout
- Quickstart (development)
  - Backend
  - Frontend
- Running (development)
- API (overview)
- Training & datasets
- Contributing
- Troubleshooting
- Acknowledgements
- License

## About
SignDetect (SLD) detects static ASL handshapes from a webcam stream, smooths predictions over a short temporal window, and builds confirmed signs into sentences. The UI supports session history, replay, and text-to-speech (TTS) for accessible demos and experimentation.

## Features
- Real-time static-sign classification with temporal smoothing
- Sentence builder with space/delete controls and session history
- Text-to-Speech (TTS) playback for translated sentences
- Responsive, accessible frontend (keyboard navigable, reduced-motion aware)
- Training helpers and dataset directory for model updates

## Tech stack
- Languages: Python (backend), JavaScript / React (frontend), CSS/HTML
- Backend: FastAPI + Uvicorn
- Frontend: Vite + React + Tailwind CSS
- Notable libraries: MediaPipe, OpenCV, numpy, ai-edge-litert (TFLite helper), gTTS, Zustand

## Repository layout
```
backend/                 # Python backend (FastAPI app, training scripts, datasets)
  app/
    main.py              # FastAPI entrypoint; registers routers and CORS
    api/                 # API endpoints (capture, predict, tts)
      capture.py
      predict.py
      tts.py
    core/                # configuration and settings
    data/                # data helpers / IO
    ml/                  # model helpers and inference utilities
    ml_models/           # saved model artifacts (ignored from git)
  datasets/              # example datasets and labels
  training/              # training scripts and notebooks
  requirements.txt       # Python dependencies
frontend/                # Vite + React UI
  public/                # static assets
  src/                   # React source
  index.html
  package.json           # npm scripts & deps
```

How it fits together: the frontend captures webcam frames and communicates with the backend (HTTP or WebSocket). The backend extracts hand landmarks (MediaPipe/OpenCV), runs the ML model to classify signs, performs temporal smoothing and decision logic, and exposes TTS endpoints to return or stream audio.

---

## Quickstart (development)

Prerequisites
- Python 3.14 (recommended for the backend environment)
- Node.js + npm
- A camera for live demo

1) Start the backend
```bash
cd backend
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Run FastAPI server (dev). For WebSocket CORS compatibility the frontend expects 127.0.0.1 in dev.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

2) Start the frontend
```bash
cd frontend
npm install
npm run dev
```
Open the Vite URL printed by the dev server (commonly http://localhost:5173) and grant camera permission when prompted.

## Running (production notes)
- Build the frontend: `cd frontend && npm run build` and serve the `dist` with any static host or integrate into the backend static files.
- Serve the backend with a production-grade ASGI server (uvicorn + process manager) and secure CORS and host settings.

## API (overview)
- GET /api/health
  - Returns health status: `{ "status": "ok" }`
- /api/capture/*
  - Endpoints related to live capture (see backend/app/api/capture.py)
- Predict endpoints (registered by the predict router)
  - Accept frame uploads and return model predictions + metadata (see backend/app/api/predict.py)
- TTS endpoints (see backend/app/api/tts.py)
  - Accept text and return/generated audio or a playable audio URL

For exact schemas, run the server and open the FastAPI docs at `http://localhost:8000/docs`.

## Training & datasets
- Example datasets and labeling helpers live under `backend/datasets`.
- Training scripts and notebooks are in `backend/training` — inspect them for preprocessing expectations (MediaPipe landmarks -> model inputs).
- Trained models should be placed in `backend/app/ml_models` or hosted externally; avoid committing large model files to git.

## Contributing
- Open an issue to discuss major changes or propose dataset/model updates.
- For code changes: fork, branch, PR. Add tests or clear reproduction steps for dataset and model updates.

## Troubleshooting
- Camera unavailable: check browser permissions and that you're running on `localhost` or HTTPS.
- WebSockets failing: ensure the backend is bound to `127.0.0.1` for local dev and CORS_ORIGINS includes your frontend host.
- Model/Inference errors: confirm model files exists and dependencies (ai-edge-litert / TFLite helpers) are installed and compatible with your platform.

## Acknowledgements
- MediaPipe for hand landmark detection
- TensorFlow Lite and tiny inference runtimes
- React, Vite, Tailwind for the frontend experience

## License
Add a LICENSE file to indicate terms (MIT recommended for demos). Currently no license file is present.

---

If you'd like, I can also:
- add a simple Dockerfile + docker-compose for one-command local setup
- create ARCHITECTURE.md with a small diagram
- open a PR with these additions instead of committing directly
