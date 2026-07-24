import argparse
from pathlib import Path
import numpy as np
import tensorflow as tf
import joblib
from sklearn.metrics import classification_report

from data_loader import load_data
from preprocessing import normalize_landmarks

def main():
    parser = argparse.ArgumentParser(description="Evaluate Sign Language Model")
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent.parent
    datasets_dir = base_dir / "datasets" / "landmarks"
    models_dir = script_dir.parent / "models"
    
    model_path = models_dir / "sign_model.keras"
    encoder_path = models_dir / "label_encoder.joblib"
    
    if not model_path.exists() or not encoder_path.exists():
        print("Model or Label Encoder not found. Please run train.py first.")
        return
        
    print("Loading data...")
    df = load_data(datasets_dir)
    if df.empty:
        print("No data found for evaluation.")
        return
        
    # Extract features
    feature_cols = [col for col in df.columns if col != 'label']
    X_raw = df[feature_cols].values.astype(np.float32)
    y_raw = df['label'].values
    
    print("Preprocessing data...")
    X = normalize_landmarks(X_raw)
    
    encoder = joblib.load(encoder_path)
    
    # Filter out labels that the encoder hasn't seen (just in case new data was collected)
    known_classes = set(encoder.classes_)
    valid_indices = [i for i, label in enumerate(y_raw) if label in known_classes]
    
    if len(valid_indices) < len(y_raw):
        print(f"Warning: Dropping {len(y_raw) - len(valid_indices)} samples with unseen labels.")
        
    X_valid = X[valid_indices]
    y_valid_raw = y_raw[valid_indices]
    
    y = encoder.transform(y_valid_raw)
    classes = encoder.classes_
    
    print("Loading model...")
    model = tf.keras.models.load_model(str(model_path))
    
    print("Evaluating...")
    y_pred_prob = model.predict(X_valid)
    y_pred = np.argmax(y_pred_prob, axis=1)
    
    print("\n" + "="*50)
    print("Evaluation Report (Full Known Dataset)")
    print("="*50)
    print(classification_report(y, y_pred, target_names=classes))

if __name__ == "__main__":
    main()
