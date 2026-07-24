import json
import numpy as np
import joblib
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from ai_edge_litert.interpreter import Interpreter

from app.ml.preprocessing import normalize_landmarks

class SignPredictor:
    """
    Singleton-style predictor class that loads the TFLite model once at startup.
    Handles inference for single frames.
    """
    def __init__(self, models_dir: str | Path = None):
        if models_dir is None:
            models_dir = Path(__file__).resolve().parent.parent / "ml_models"
        else:
            models_dir = Path(models_dir)
            
        tflite_path = models_dir / "sign_model.tflite"
        encoder_path = models_dir / "label_encoder.joblib"
        
        if not tflite_path.exists():
            raise FileNotFoundError(f"TFLite model not found at {tflite_path}")
        if not encoder_path.exists():
            raise FileNotFoundError(f"Label encoder not found at {encoder_path}")
            
        # Load TFLite Model
        self.interpreter = Interpreter(model_path=str(tflite_path))
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load Label Encoder
        self.encoder = joblib.load(encoder_path)
        self.classes = self.encoder.classes_

    def predict(self, landmarks_data: List[List[List[float]]]) -> Tuple[Optional[str], float, List[Dict[str, Any]]]:
        """
        Takes raw landmarks from HandDetector and returns predictions.
        
        Args:
            landmarks_data: list of hands, where each hand is a list of 21 [x,y,z] coordinates.
            
        Returns:
            (predicted_label, confidence, top_3_predictions)
            If no hand is detected, returns ("no_hand", 0.0, [])
        """
        if not landmarks_data or len(landmarks_data) == 0:
            return "no_hand", 0.0, []
            
        # Extract the first hand's landmarks (we currently only support single-hand inference)
        hand_points = landmarks_data[0]
        
        # Flatten from [[x0, y0, z0], [x1, y1, z1], ...] to [x0, y0, z0, x1, y1, z1, ...]
        flattened = [coord for point in hand_points for coord in point]
        
        # Convert to numpy array and shape (1, 63)
        features_raw = np.array([flattened], dtype=np.float32)
        
        # Preprocess
        features_normalized = normalize_landmarks(features_raw)
        
        # Ensure it's float32 for TFLite
        input_data = features_normalized.astype(np.float32)
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # output_data is shape (1, num_classes) containing softmax probabilities
        probabilities = output_data[0]
        
        # Get top 3 predictions
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        
        top_3_predictions = []
        for idx in top_3_indices:
            label = str(self.classes[idx])
            conf = float(probabilities[idx])
            top_3_predictions.append({"label": label, "confidence": conf})
            
        best_label = top_3_predictions[0]["label"]
        best_conf = top_3_predictions[0]["confidence"]
        
        return best_label, best_conf, top_3_predictions
