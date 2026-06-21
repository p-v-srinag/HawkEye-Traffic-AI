import cv2
import numpy as np
import logging
import easyocr
from app.modules.ocr.validation import validate_plate

class PlateOCR:
    def __init__(self):
        # Initialize EasyOCR for English, keeping it in memory for fast inference
        # EasyOCR is highly robust against blurry or low-res license plates.
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    def extract_and_validate(self, image_path: str, bbox: list):
        """
        Extracts plate from image using YOLO bbox, performs OCR, and validates.
        """
        image = cv2.imread(image_path)
        if image is None:
            return {"status": "ERROR", "plate": "IMAGE_NOT_FOUND"}

        x1, y1, x2, y2 = map(int, bbox)
        
        # Add a dynamic 5px margin to ensure the whole plate is captured
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

        # Convert to Grayscale for enhanced OCR contrast (Advanced OCR Pipeline)
        plate_gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

        # Use EasyOCR to read the text directly from the numpy array crop
        # detail=0 returns just the strings
        results = self.reader.readtext(plate_gray, detail=0)

        if not results:
            # Fallback
            return {"status": "MANUAL_REVIEW", "plate": "NOT_AVAILABLE"}

        # Combine all detected text fragments
        raw_text = "".join(results).replace(" ", "")

        # Pass through the Tolerant SEVE Validation Engine
        validation_result = validate_plate(raw_text)
        
        return validation_result