import cv2
import requests
import urllib.request
import os
import sys

API_URL = "http://localhost:8000/api/capture/frame"
LABEL = "A"

def get_hand_image():
    # Try webcam first
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Successfully captured image from webcam.")
            cap.release()
            return frame
    print("Webcam not available or failed to read frame. Downloading sample image...")
    
    # Download sample image
    # We will use a known sample image from MediaPipe github for hand landmarks
    sample_url = "https://raw.githubusercontent.com/google/mediapipe/master/mediapipe/docs/images/mobile/hand_tracking_3d_android_gpu.gif"
    # Actually, a static image is better. Let's use a standard test image from mediapipe's tests
    sample_url = "https://raw.githubusercontent.com/google/mediapipe/master/mediapipe/tasks/testdata/vision/hand_landmarks.jpg"
    
    img_path = "sample_hand.jpg"
    if not os.path.exists(img_path):
        urllib.request.urlretrieve(sample_url, img_path)
    
    frame = cv2.imread(img_path)
    if frame is None:
        print("Failed to load sample image.")
        sys.exit(1)
    
    return frame

def main():
    frame = get_hand_image()
    
    # Encode frame to jpg
    ret, encoded_image = cv2.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode image")
        sys.exit(1)
        
    # Send via multipart POST
    files = {
        'file': ('test_hand.jpg', encoded_image.tobytes(), 'image/jpeg')
    }
    data = {
        'label': LABEL
    }
    
    print(f"Sending POST to {API_URL} with label={LABEL}...")
    try:
        response = requests.post(API_URL, files=files, data=data)
        print(f"Response status: {response.status_code}")
        print("Raw JSON response:")
        print(response.text)
        
        # Verify label count
        labels_url = "http://localhost:8000/api/capture/labels"
        print(f"\nChecking GET {labels_url}...")
        resp_labels = requests.get(labels_url)
        print(f"Response status: {resp_labels.status_code}")
        print(resp_labels.text)
        
    except requests.exceptions.ConnectionError:
        print(f"Connection error to {API_URL}. Is uvicorn running?")
        sys.exit(1)

if __name__ == "__main__":
    main()
