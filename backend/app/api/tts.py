from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
import io

router = APIRouter()

class TTSRequest(BaseModel):
    text: str

@router.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Converts text to speech using Google TTS and returns an MP3 audio stream.
    """
    text = request.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Text is too long (max 500 characters)")
        
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to in-memory buffer
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        
        # Reset pointer to start of stream
        audio_fp.seek(0)
        
        return StreamingResponse(audio_fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
