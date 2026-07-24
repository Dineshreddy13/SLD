from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from app.data.dataset_capture import DatasetCapture

router = APIRouter()
capture_service = DatasetCapture(base_dir="datasets")

@router.post("/frame")
async def capture_frame(label: str = Form(...), file: UploadFile = Form(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")
        
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode the image.")
        
    result = capture_service.process_and_save(frame, label)
    return JSONResponse(content=result)

@router.get("/labels")
async def get_labels():
    stats = capture_service.get_stats()
    return {"labels": list(stats.keys()), "counts": stats}
