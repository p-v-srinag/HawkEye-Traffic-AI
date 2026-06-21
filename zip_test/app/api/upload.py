from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

import shutil
import os

router = APIRouter()

UPLOAD_DIR = "data/uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    filepath = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "filename": file.filename,
        "path": filepath
    }

from typing import List

@router.post("/upload_burst")
async def upload_burst(
    files: List[UploadFile] = File(...)
):
    """
    Evidence Burst Upload: Accepts a sequence of images (burst) to evaluate
    temporal violations like Wrong Side Driving and Illegal Parking without video.
    """
    saved_paths = []
    for file in files:
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(filepath)

    return {
        "files_received": len(files),
        "paths": saved_paths
    }