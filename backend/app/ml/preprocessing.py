import numpy as np

def normalize_landmarks(features: np.ndarray) -> np.ndarray:
    """
    Normalizes the 63 hand landmarks relative to the wrist (landmark 0).
    
    CRITICAL: This MUST stay in sync with training/scripts/preprocessing.py!
    Any mismatch here will silently break prediction accuracy.
    
    Why this matters:
    1. Translation Invariance: By subtracting the wrist coordinates (x0, y0, z0) 
       from all other landmarks, the hand's absolute position in the camera frame 
       doesn't matter. A hand in the top-left will look the same as a hand in the 
       bottom-right to the model.
    2. Scale Invariance: By dividing the coordinates by the 
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
