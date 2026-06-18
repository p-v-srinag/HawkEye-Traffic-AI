from fastapi import APIRouter

from app.services.detection_service import (
    process_detection
)

router = APIRouter()


@router.get("/detect")
def detect():

    image_path = (
        "data/uploads/image.png"
    )

    result = process_detection(
        image_path
    )

    return result