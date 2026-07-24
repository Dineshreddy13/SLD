import os
import time
import base64
import csv
import cv2
import numpy as np
from pathlib import Path
from app.vision.hand_detector import HandDetector

class DatasetCapture:
    def __init__(self, base_dir: str = "datasets"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.landmarks_dir = self.base_dir / "landmarks"
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.landmarks_dir.mkdir(parents=True, exist_ok=True)
        
        self.detector = HandDetector(static_image_mode=True)

    def process_and_save(self, frame: np.ndarray, label: str):
        """
        Process an image, extract hand landmarks, and save if valid.
        """
        label = label.upper().strip()
        
        # Ensure label directory exists
        label_dir = self.images_dir / label
        label_dir.mkdir(parents=True, exist_ok=True)
        
        landmarks_data, handedness_data, annotated_frame = self.detector.process_frame(frame)
        
        if not landmarks_data:
            return {
                "success": False,
                "message": "No hands detected in the frame.",
                "label": label,
                "landmarks": None,
                "annotated_image_base64": self._frame_to_base64(annotated_frame)
            }
            
        # We take the first hand detected for simplicity in dataset creation
        hand_points = landmarks_data[0]
        flattened_points = [coord for point in hand_points for coord in point]
        
        # Save image
        timestamp = int(time.time() * 1000)
        image_filename = f"{timestamp}.jpg"
        image_path = label_dir / image_filename
        cv2.imwrite(str(image_path), frame)
        
        # Save landmarks
        csv_path = self.landmarks_dir / f"{label}.csv"
        file_exists = csv_path.exists()
        
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                # Create headers: x0, y0, z0, ... x20, y20, z20
                headers = []
                for i in range(21):
                    headers.extend([f"x{i}", f"y{i}", f"z{i}"])
                writer.writerow(["image_file"] + headers)
                
            writer.writerow([image_filename] + flattened_points)
            
        return {
            "success": True,
            "message": "Data saved successfully.",
            "label": label,
            "landmarks": flattened_points,
            "annotated_image_base64": self._frame_to_base64(annotated_frame)
        }

    def get_stats(self):
        """
        Returns stats about the collected dataset.
        """
        stats = {}
        if not self.landmarks_dir.exists():
            return stats
            
        for csv_file in self.landmarks_dir.glob("*.csv"):
            label = csv_file.stem
            with open(csv_file, 'r') as f:
                row_count = sum(1 for row in f) - 1 # subtract header
            stats[label] = row_count
        return stats

    def _frame_to_base64(self, frame: np.ndarray) -> str:
        _, buffer = cv2.imencode('.jpg', frame)
        base64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"
