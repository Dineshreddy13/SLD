import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path
from typing import Tuple

def normalize_landmarks(features: np.ndarray) -> np.ndarray:
    """
    Normalizes the 63 hand landmarks relative to the wrist (landmark 0).
    
    Why this matters:
    1. Translation Invariance: By subtracting the wrist coordinates (x0, y0, z0) 
       from all other landmarks, the hand's absolute position in the camera frame 
       doesn't matter. A hand in the top-left will look the same as a hand in the 
       bottom-right to the model.
    2. Scale Invariance (Optional/Applied here): By dividing the coordinates by the 
       distance between the wrist (landmark 0) and the middle finger MCP (landmark 9),
       the size of the hand (or its distance from the camera) doesn't affect the model.
       
    Args:
        features: numpy array of shape (N, 63) containing raw landmarks.
        
    Returns:
        Normalized numpy array of shape (N, 63).
    """
    # Extract wrist and middle MCP coordinates
    # shape: (N, 3)
    wrist = features[:, 0:3]
    mid_mcp = features[:, 27:30]
    
    # Calculate scale as the Euclidean distance between wrist and middle MCP
    scale = np.linalg.norm(mid_mcp - wrist, axis=1, keepdims=True)
    scale = np.where(scale == 0, 1.0, scale) # Avoid division by zero
    
    # Reshape features to (N, 21, 3) for vectorized operations
    reshaped_features = features.reshape(-1, 21, 3)
    reshaped_wrist = wrist.reshape(-1, 1, 3)
    reshaped_scale = scale.reshape(-1, 1, 1)
    
    # Translate and scale
    translated = reshaped_features - reshaped_wrist
    normalized = translated / reshaped_scale
    
    # Flatten back to (N, 63)
    return normalized.reshape(-1, 63)

def preprocess_data(df: pd.DataFrame, models_dir: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, LabelEncoder]:
    """
    Normalizes features, encodes labels, and splits into train/val/test.
    """
    # Extract features and labels
    feature_cols = [col for col in df.columns if col != 'label']
    X_raw = df[feature_cols].values.astype(np.float32)
    y_raw = df['label'].values
    
    # Normalize features
    X = normalize_landmarks(X_raw)
    
    # Encode labels to integers
    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)
    
    # Save the encoder for inference later
    models_dir.mkdir(parents=True, exist_ok=True)
    encoder_path = models_dir / "label_encoder.joblib"
    joblib.dump(encoder, encoder_path)
    print(f"Saved label encoder to {encoder_path}")
    
    # Stratified split: 70% train, 15% val, 15% test
    # First split 85% train_val, 15% test
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, stratify=y, random_state=42)
    
    # Then split the 85% into 70% train and 15% val
    # 0.15 / 0.85 ≈ 0.1765
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.17647, stratify=y_temp, random_state=42)
    
    return X_train, X_val, X_test, y_train, y_val, y_test, encoder
