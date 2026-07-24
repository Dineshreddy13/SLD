import argparse
import json
import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

from data_loader import load_data, print_summary
from preprocessing import preprocess_data
from model import build_model

def plot_history(history, models_dir: Path):
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.legend()
    plt.title('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Train Acc')
    plt.plot(history.history['val_accuracy'], label='Val Acc')
    plt.legend()
    plt.title('Accuracy')
    
    plt.tight_layout()
    plt.savefig(models_dir / "training_history.png")
    plt.close()

def plot_confusion_matrix(y_true, y_pred, classes, models_dir: Path):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(models_dir / "confusion_matrix.png")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Train Sign Language Model")
    parser.add_argument('--epochs', type=int, default=100, help="Number of training epochs")
    parser.add_argument('--batch-size', type=int, default=32, help="Batch size")
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent.parent
    datasets_dir = base_dir / "datasets" / "landmarks"
    models_dir = script_dir.parent / "models"
    
    # 1. Load Data
    print("Loading data...")
    df = load_data(datasets_dir)
    if df.empty:
        print("Cannot train without data. Exiting.")
        return
        
    print_summary(df)
    
    # 2. Preprocess Data
    print("Preprocessing data...")
    X_train, X_val, X_test, y_train, y_val, y_test, encoder = preprocess_data(df, models_dir)
    
    classes = encoder.classes_
    num_classes = len(classes)
    input_dim = X_train.shape[1]
    
    # 3. Build Model
    print("Building model...")
    model = build_model(input_dim=input_dim, num_classes=num_classes)
    model.summary()
    
    # 4. Train Model
    models_dir.mkdir(parents=True, exist_ok=True)
    keras_model_path = models_dir / "sign_model.keras"
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ModelCheckpoint(filepath=str(keras_model_path), monitor='val_loss', save_best_only=True)
    ]
    
    print(f"Training model for {args.epochs} epochs with batch size {args.batch_size}...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks
    )
    
    # Plot history
    plot_history(history, models_dir)
    
    # 5. Evaluate
    print("Evaluating on test set...")
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
    
    y_pred_prob = model.predict(X_test)
    y_pred = np.argmax(y_pred_prob, axis=1)
    
    print("\nClassification Report (Test Set):")
    report = classification_report(y_test, y_pred, target_names=classes)
    print(report)
    
    plot_confusion_matrix(y_test, y_pred, classes, models_dir)
    
    # 6. Save Artifacts
    # Save metadata
    metadata = {
        "classes": list(classes),
        "input_dim": input_dim,
        "normalization": "Translation (relative to wrist) and Scale (distance from wrist to mid MCP)",
        "training_date": datetime.datetime.now().isoformat(),
        "test_accuracy": float(accuracy),
        "tf_version": tf.__version__
    }
    with open(models_dir / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
        
    # Convert and save TFLite model
    print("Exporting TFLite model...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open(models_dir / "sign_model.tflite", "wb") as f:
        f.write(tflite_model)
        
    print(f"\nTraining complete. All artifacts saved to {models_dir}")

if __name__ == "__main__":
    main()
