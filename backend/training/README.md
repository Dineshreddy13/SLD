# Sign Language Model Training Pipeline

This directory contains the machine learning pipeline to train a gesture recognition model based on the data collected in the `datasets/` folder.

## Folder Structure
- `scripts/`: Python scripts for data loading, preprocessing, training, and evaluation.
- `models/`: Output artifacts (saved models, metrics, encoders) are automatically saved here after training.
- `notebooks/`: Optional workspace for Jupyter notebooks or experimentation.

## Setup
Ensure that you have set up `train_venv` with Python 3.11 and the required dependencies as outlined in `requirements.txt`.

## Order of Operations

### 1. Collect Data (Main App Environment)
First, you must collect a dataset using the standalone collector script. Ensure your **main app's virtual environment** (Python 3.14) is activated, then run from the `backend/` directory:
```bash
.\.venv\Scripts\python scripts\collect_dataset.py
```

### 2. Train Model (Training Environment)
Once data is collected, switch to the **isolated training environment** (Python 3.11). From the `backend/` directory, run:
```bash
.\train_venv\Scripts\python training\scripts\train.py
```
*Optional arguments: `--epochs 100 --batch-size 32`*
   
This script will:
- Load the landmark CSVs.
- Preprocess the data (normalize by translation and scale).
- Train a lightweight Dense neural network.
- Save the trained model (`sign_model.keras`), `label_encoder.joblib`, and `model_metadata.json` to the `models/` directory.
- Generate confusion matrices and training history plots.
- Export a highly efficient `sign_model.tflite` model (which the main FastAPI app will use for inference).

### 3. Evaluate Model (Training Environment)
To quickly evaluate an already-trained model without retraining:
```bash
.\train_venv\Scripts\python training\scripts\evaluate.py
```

## Artifacts Explained (`training/models/`)
- `sign_model.keras`: The full Keras SavedModel format containing architecture and weights.
- `sign_model.tflite`: The compressed TensorFlow Lite model optimized for CPU inference in the backend.
- `label_encoder.joblib`: The scikit-learn `LabelEncoder` used to map string labels to integer classes. This is necessary for translating predictions back to letters during inference.
- `model_metadata.json`: Contains useful information about the training run, input dimensions, and classes.
- `confusion_matrix.png` / `training_history.png`: Visual evaluation of model performance across epochs and classes.

## Known Limitation: J and Z
**Important:** ASL letters **J** and **Z** are dynamic, motion-based signs that cannot be accurately represented by a single static frame of hand landmarks. 

Because v1 of this project uses a static feedforward classifier architecture, J and Z are **intentionally excluded** from the training pipeline and the default dataset collection cycle. This is a documented, standard limitation (also seen in the popular Kaggle ASL Alphabet dataset). 

Supporting motion-based signs would require a sequence-based model architecture (e.g., LSTMs or Transformers tracking multiple frames over time). This is a documented future enhancement rather than an oversight.
