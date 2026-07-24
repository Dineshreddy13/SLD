import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pathlib import Path

class HandDetector:
    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        model_path = Path(__file__).parent.parent.parent / "hand_landmarker.task"
        
        # If the model file is not found, fallback to graceful erroring or just raise.
        if not model_path.exists():
            raise FileNotFoundError(f"MediaPipe task model not found at {model_path}")

        base_options = python.BaseOptions(model_asset_path=str(model_path))
        
        # Determine the running mode
        running_mode = vision.RunningMode.IMAGE if static_image_mode else vision.RunningMode.VIDEO
        # Since we use this for single uploaded frames, IMAGE mode is best.
        # But if it's not static, we might want to use VIDEO, but that requires timestamps.
        # For our use case (POST /frame), it's always IMAGE.
        running_mode = vision.RunningMode.IMAGE

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=running_mode,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def process_frame(self, frame: np.ndarray):
        """
        Process a single frame and return landmarks, handedness, and annotated frame.
        """
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Process the image
        detection_result = self.detector.detect(mp_image)

        annotated_frame = frame.copy()
        landmarks_data = []
        handedness_data = []

        if detection_result.hand_landmarks:
            for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                # Save handedness
                handedness = detection_result.handedness[idx][0].category_name
                handedness_data.append(handedness)
                
                # Save landmarks
                hand_points = []
                for lm in hand_landmarks:
                    hand_points.append([lm.x, lm.y, lm.z])
                landmarks_data.append(hand_points)

                # Draw landmarks manually since we don't have drawing_utils easily with Tasks API
                HAND_CONNECTIONS = [
                    (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
                    (0, 5), (5, 6), (6, 7), (7, 8), # Index
                    (5, 9), (9, 10), (10, 11), (11, 12), # Middle
                    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
                    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Pinky + palm
                ]

                # Convert to pixel coordinates
                h, w, _ = annotated_frame.shape
                pixel_points = []
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    pixel_points.append((cx, cy))
                    cv2.circle(annotated_frame, (cx, cy), 4, (0, 255, 0), cv2.FILLED)
                    
                # Draw connections
                for connection in HAND_CONNECTIONS:
                    pt1 = pixel_points[connection[0]]
                    pt2 = pixel_points[connection[1]]
                    cv2.line(annotated_frame, pt1, pt2, (255, 0, 0), 2)

        return landmarks_data, handedness_data, annotated_frame
