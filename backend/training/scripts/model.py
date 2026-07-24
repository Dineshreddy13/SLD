import tensorflow as tf
from tensorflow.keras import layers, models

def build_model(input_dim: int = 63, num_classes: int = 34) -> tf.keras.Model:
    """
    Builds a lightweight feedforward neural network for landmark classification.
    
    Note: This model currently supports 34 static classes (A-I, K-Y, 0-9).
    Dynamic signs 'J' and 'Z' are intentionally excluded because this is a 
    static, single-frame architecture.

    
    This is not an image classification task, so a CNN is unnecessary. We are 
    learning directly from 3D coordinates, which makes a small Dense network 
    highly efficient and effective.
    """
    model = models.Sequential([
        layers.Input(shape=(input_dim,)),
        
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(32, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # We use sparse_categorical_crossentropy because labels are integer encoded,
    # not one-hot encoded.
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model
