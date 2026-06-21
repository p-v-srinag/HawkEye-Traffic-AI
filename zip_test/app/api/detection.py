import os
from fastapi import APIRouter
from app.services.detection_service import process_detection

router = APIRouter()

@router.get("/detect")
def detect():
    upload_dir = "data/uploads"
    
    # Get the most recently uploaded file in the directory
    try:
        files = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
        if not files:
            return {"status": "FAILED", "message": "No images found in upload directory."}
            
        latest_file = max(files, key=os.path.getctime)
    except Exception as e:
         return {"status": "FAILED", "message": f"File system error: {str(e)}"}

    # Pass the actual uploaded image to the SEVE and YOLO pipeline
    result = process_detection(latest_file)

    return result

from pydantic import BaseModel
from typing import List
from app.services.detection_service import process_burst_detection

class BurstRequest(BaseModel):
    paths: List[str]

@router.post("/detect_burst")
def detect_burst(request: BurstRequest):
    if not request.paths:
        return {"status": "FAILED", "message": "No paths provided for burst detection."}
        
    try:
        result = process_burst_detection(request.paths)
        return result
    except Exception as e:
        return {"status": "FAILED", "message": str(e)}