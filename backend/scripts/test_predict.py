import requests
import sys
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent.parent
    
    # Try to find an existing image in datasets/images/A/
    images_dir = base_dir / "datasets" / "images" / "A"
    
    image_path = None
    if images_dir.exists():
        images = list(images_dir.glob("*.jpg"))
        if images:
            image_path = images[0]
            
    if not image_path:
        print("No collected images found. Please run collect_dataset.py first.")
        sys.exit(1)
        
    print(f"Testing with image: {image_path}")
    
    url = "http://127.0.0.1:8000/api/predict/frame"
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/jpeg")}
            response = requests.post(url, files=files)
            
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        import json
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is FastAPI running on port 8000?")
        
if __name__ == "__main__":
    main()
