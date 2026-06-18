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