from collections import deque
from typing import Optional, Tuple

class PredictionSmoother:
    def __init__(self, window_size: int = 15, confidence_threshold: float = 0.7):
        self.window_size = window_size
        self.confidence_threshold = confidence_threshold
        
        self.history = deque(maxlen=window_size)
        
        # Track what the current stable letter is, so we only emit `is_new_confirmation = True` 
        # when a NEW stable letter is established.
        self.current_stable_label: Optional[str] = None
        
    def add_prediction(self, label: str, confidence: float) -> Tuple[Optional[str], bool]:
        """
        Adds a single-frame prediction to the smoothing window.
        
        Args:
            label: The raw predicted string label (e.g., 'A').
            confidence: The softmax probability of that label.
            
        Returns:
            (stable_label, is_new_confirmation)
            - stable_label: The string label if the window meets the stability criteria, else None.
            - is_new_confirmation: True ONLY if this frame caused the stable_label to transition 
              from None (or a different letter) to this new letter.
        """
        # Exclude low confidence noise from the history entirely
        if confidence < 0.2:
            self.history.append(("no_hand", 0.0))
        else:
            self.history.append((label, confidence))
            
        if len(self.history) < self.window_size:
            return None, False
            
        # Count frequencies in the window
        label_counts = {}
        label_conf_sums = {}
        
        for l, c in self.history:
            if l == "no_hand":
                continue
            label_counts[l] = label_counts.get(l, 0) + 1
            label_conf_sums[l] = label_conf_sums.get(l, 0.0) + c
            
        if not label_counts:
            # If everything was no_hand
            self.current_stable_label = None
            return None, False
            
        # Find majority label
        majority_label = max(label_counts.items(), key=lambda x: x[1])[0]
        majority_count = label_counts[majority_label]
        
        # Must be more than 50% of the window
        if majority_count < (self.window_size // 2):
            self.current_stable_label = None
            return None, False
            
        # Check average confidence of the majority label
        avg_confidence = label_conf_sums[majority_label] / majority_count
        if avg_confidence < self.confidence_threshold:
            self.current_stable_label = None
            return None, False
            
        # We have a stable label!
        is_new = False
        if self.current_stable_label != majority_label:
            is_new = True
            self.current_stable_label = majority_label
            
        return majority_label, is_new

    def reset(self):
        """Clears the sliding window and stable state."""
        self.history.clear()
        self.current_stable_label = None
