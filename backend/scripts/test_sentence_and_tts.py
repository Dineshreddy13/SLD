import sys
import os
from pathlib import Path
import requests

# Add backend directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.sentence_builder import SentenceBuilder

def test_sentence_builder():
    print("--- Testing SentenceBuilder ---")
    sb = SentenceBuilder()
    
    # Test letters
    sb.add_letter("H")
    sb.add_letter("E")
    sb.add_letter("L")
    sb.add_letter("L")
    sb.add_letter("O")
    print(f"After letters: '{sb.get_sentence()}'")
    
    # Test space
    sb.add_space()
    print(f"After space: '{sb.get_sentence()}'")
    
    # Test double space (should not add second space)
    sb.add_space()
    print(f"After double space: '{sb.get_sentence()}'")
    
    # Test more letters
    sb.add_letter("W")
    sb.add_letter("O")
    sb.add_letter("R")
    sb.add_letter("L")
    sb.add_letter("D")
    sb.add_letter("Z") # accidental Z
    print(f"After more letters: '{sb.get_sentence()}'")
    
    # Test delete
    sb.delete_last()
    print(f"After delete_last: '{sb.get_sentence()}'")
    
    # Test clear
    sb.clear()
    print(f"After clear: '{sb.get_sentence()}'")
    print("SentenceBuilder tests passed!\n")

def test_tts_endpoint():
    print("--- Testing TTS Endpoint ---")
    url = "http://127.0.0.1:8000/api/tts"
    payload = {"text": "HELLO WORLD"}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            output_file = Path(__file__).resolve().parent / "test_output.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            size = output_file.stat().st_size
            print(f"Audio file saved to {output_file.name} (Size: {size} bytes)")
            if size > 0:
                print("TTS test passed!")
            else:
                print("TTS test failed: File is empty.")
        else:
            print(f"TTS request failed: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Ensure FastAPI is running on port 8000.")

if __name__ == "__main__":
    test_sentence_builder()
    test_tts_endpoint()
