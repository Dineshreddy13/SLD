import cv2
import sys
import os
import time
import csv
from pathlib import Path

# Add backend directory to sys.path so we can import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.vision.hand_detector import HandDetector

def get_stats(landmarks_dir: Path):
    """Calculate the number of samples collected for each label."""
    stats = {}
    if not landmarks_dir.exists():
        return stats
    for csv_file in landmarks_dir.glob("*.csv"):
        label = csv_file.stem
        try:
            with open(csv_file, 'r') as f:
                # Count rows and subtract header
                row_count = sum(1 for _ in f) - 1
            if row_count > 0:
                stats[label] = row_count
        except Exception:
            pass
    return stats

def main():
    print("Initializing HandDetector...")
    try:
        detector = HandDetector()
    except Exception as e:
        print(f"Error initializing HandDetector: {e}")
        return

    # Attempt to open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        print("Please check if your webcam is connected and accessible.")
        return

    # Setup directories
    base_dir = Path("datasets")
    images_dir = base_dir / "images"
    landmarks_dir = base_dir / "landmarks"
    images_dir.mkdir(parents=True, exist_ok=True)
    landmarks_dir.mkdir(parents=True, exist_ok=True)

    # Setup labels list (A-Z, 0-9), excluding dynamic signs J and Z
    all_letters = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    labels = [c for c in all_letters if c not in ('J', 'Z')] + [str(i) for i in range(10)]
    current_label_idx = 0
    current_label = labels[current_label_idx]

    burst_mode = False
    last_burst_time = 0
    BURST_INTERVAL = 0.2  # seconds

    stats = get_stats(landmarks_dir)
    
    instructions_console = """
==================================================
Sign Language Dataset Collector
==================================================
Instructions:
 - Press A-Z or 0-9 to set the current label.
 - Press SPACE to capture a single sample.
 - Press 'B' to toggle Burst Mode (auto-captures every ~200ms).
 - Press 'N' to cycle to the next suggested label.
 - Press 'Q' or ESC to quit.
==================================================
"""
    print(instructions_console)

    msg = ""
    msg_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame from webcam. Exiting...")
            break

        # Mirror the frame for a more natural preview
        frame = cv2.flip(frame, 1)
        
        # Process the frame to find hands
        landmarks_data, handedness_data, annotated_frame = detector.process_frame(frame)
        
        hand_detected = len(landmarks_data) > 0
        current_time = time.time()
        
        # Draw Overlay
        cv2.putText(annotated_frame, f"Current label: {current_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        count = stats.get(current_label, 0)
        cv2.putText(annotated_frame, f"Samples: {count}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        burst_color = (0, 0, 255) if burst_mode else (255, 255, 255)
        cv2.putText(annotated_frame, f"Burst Mode: {'ON' if burst_mode else 'OFF'}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, burst_color, 2)
        
        instructions_screen = "Press a letter/number key to set label | SPACE = capture | B = burst | Q = quit | N = next"
        cv2.putText(annotated_frame, instructions_screen, (10, annotated_frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # Draw transient message (e.g., "Captured!" or "No hand detected")
        if current_time - msg_time < 0.8:
            cv2.putText(annotated_frame, msg, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

        cv2.imshow("Dataset Collector", annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == 27:  # Q or ESC
            break
        elif key == ord('n'):
            current_label_idx = (current_label_idx + 1) % len(labels)
            current_label = labels[current_label_idx]
        elif key == ord('b'):
            burst_mode = not burst_mode
            msg = "Burst Mode ON" if burst_mode else "Burst Mode OFF"
            msg_time = current_time
        elif key >= ord('a') and key <= ord('z'):
            current_label = chr(key).upper()
            if current_label in ['J', 'Z']:
                msg = "Warning: J/Z unsupported (motion)"
                msg_time = current_time
                print("\nWARNING: J and Z are motion-based signs and not supported in this version. "
                      "Data will still be saved if you proceed, but the training pipeline should exclude these classes.\n")
                
            if current_label in labels:
                current_label_idx = labels.index(current_label)
        elif key >= ord('0') and key <= ord('9'):
            current_label = chr(key)
            if current_label in labels:
                current_label_idx = labels.index(current_label)
        
        # Determine if we should capture this frame
        capture_triggered = (key == ord(' ')) or (burst_mode and (current_time - last_burst_time) >= BURST_INTERVAL)
        
        if capture_triggered:
            if not hand_detected:
                if key == ord(' '):  # Only show warning if manually pressed
                    msg = "No hand detected"
                    msg_time = current_time
            else:
                # Save image and landmarks (use the raw frame for the saved image)
                hand_points = landmarks_data[0] # taking the first hand
                flattened_points = [coord for point in hand_points for coord in point]
                
                timestamp = int(time.time() * 1000)
                image_filename = f"{timestamp}.jpg"
                
                label_dir = images_dir / current_label
                label_dir.mkdir(parents=True, exist_ok=True)
                image_path = label_dir / image_filename
                
                cv2.imwrite(str(image_path), frame)
                
                csv_path = landmarks_dir / f"{current_label}.csv"
                file_exists = csv_path.exists()
                
                with open(csv_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        # Write header if file is new
                        headers = []
                        for i in range(21):
                            headers.extend([f"x{i}", f"y{i}", f"z{i}"])
                        writer.writerow(["image_file"] + headers)
                    writer.writerow([image_filename] + flattened_points)
                
                stats[current_label] = stats.get(current_label, 0) + 1
                last_burst_time = current_time
                msg = "Captured!"
                msg_time = current_time

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

    # Print Summary
    print("\n" + "="*50)
    print("Collection Summary:")
    print("="*50)
    
    total_samples = 0
    final_stats = get_stats(landmarks_dir)
    if not final_stats:
        print("No samples collected yet.")
    else:
        for label in sorted(final_stats.keys()):
            count = final_stats[label]
            print(f"Label {label}: {count} samples")
            total_samples += count
    print("="*50)
    print(f"Total samples across all labels: {total_samples}")

if __name__ == "__main__":
    main()
