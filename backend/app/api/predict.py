from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
import cv2
import numpy as np

from app.vision.hand_detector import HandDetector
from app.ml.predictor import SignPredictor
from app.ml.temporal_smoothing import PredictionSmoother
from app.core.sentence_builder import SentenceBuilder
import json

router = APIRouter()

# Global instances loaded once at startup
detector = HandDetector()
predictor = SignPredictor()

@router.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    # Each connection gets its own smoother state
    smoother = PredictionSmoother(window_size=15, confidence_threshold=0.7)
    sentence_builder = SentenceBuilder()
    
    try:
        while True:
            message = await websocket.receive()
            
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    action = data.get("action")
                    if action == "space":
                        sentence_builder.add_space()
                    elif action == "delete":
                        sentence_builder.delete_last()
                    elif action == "clear":
                        sentence_builder.clear()
                        smoother.reset()
                except Exception:
                    pass
                    
                await websocket.send_json({
                    "raw_prediction": None,
                    "stable_prediction": None,
                    "hand_detected": False,
                    "sentence": sentence_builder.get_sentence()
                })
                continue
                
            if "bytes" in message:
                data = message["bytes"]
            
            # Decode image
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await websocket.send_json({"error": "Failed to decode frame"})
                continue
                
            # Find hands
            landmarks_data, _, _ = detector.process_frame(frame)
            
            # Predict
            raw_label, confidence, _ = predictor.predict(landmarks_data)
            hand_detected = raw_label != "no_hand"
            
            # Smooth
            stable_label, is_new = smoother.add_prediction(raw_label, confidence)
            
            if is_new and stable_label and stable_label != "no_hand":
                sentence_builder.add_letter(stable_label)
            
            # Respond
            await websocket.send_json({
                "raw_prediction": {
                    "label": raw_label if hand_detected else None,
                    "confidence": float(confidence) if hand_detected else 0.0
                },
                "stable_prediction": {
                    "label": stable_label,
                    "is_new": is_new
                },
                "hand_detected": hand_detected,
                "sentence": sentence_builder.get_sentence()
            })
            
    except WebSocketDisconnect:
        print("Client disconnected from /ws/predict")
    except Exception as e:
        print(f"Error in websocket_predict: {e}")
        try:
            await websocket.close()
        except:
            pass

@router.post("/api/predict/frame")
async def predict_frame(file: UploadFile = File(...)):
    """
    Stateless REST endpoint for a single frame. 
    Does not use temporal smoothing.
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        return {"error": "Failed to decode image"}
        
    landmarks_data, _, _ = detector.process_frame(frame)
    raw_label, confidence, top_3 = predictor.predict(landmarks_data)
    
    return {
        "hand_detected": raw_label != "no_hand",
        "predicted_label": raw_label if raw_label != "no_hand" else None,
        "confidence": float(confidence),
        "top_3": top_3
    }
