import cv2
import numpy as np
import logging
from paddleocr import PaddleOCR
from app.modules.ocr.validation import validate_plate

# Suppress PaddleOCR's noisy terminal output natively
logging.getLogger("ppocr").setLevel(logging.ERROR)

class PlateOCR:
    def __init__(self):
        # Removed the deprecated 'show_log' parameter
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

    def extract_and_validate(self, image_path: str, bbox: list):
        """
        Extracts plate from image using YOLO bbox, performs OCR, and validates.
        """
        image = cv2.imread(image_path)
        if image is None:
            return {"status": "ERROR", "plate": "IMAGE_NOT_FOUND"}

        x1, y1, x2, y2 = map(int, bbox)
        
        # Add a dynamic margin to ensure the whole plate is captured
        h, w, _ = image.shape
        margin = 5
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(w, x2 + margin)
        y2 = min(h, y2 + margin)

        # Crop the plate region
        plate_crop = image[y1:y2, x1:x2]

        if plate_crop.size == 0:
             return {"status": "ERROR", "plate": "INVALID_CROP"}

        # Convert to Grayscale to improve OCR accuracy under varying traffic lights
        gray_plate = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

        # Run PaddleOCR specifically on the cropped region
        results = self.ocr.ocr(gray_plate, cls=True)

        if not results or not results[0]:
            return {"status": "MANUAL_REVIEW", "plate": "UNREADABLE"}

        # Extract highest confidence text
        texts = [line[1][0] for line in results[0]]
        raw_text = "".join(texts)

        # Pass through the SEVE Validation Engine
        validation_result = validate_plate(raw_text)
        
        return validation_result