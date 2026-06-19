import os
from app.modules.detection.yolo_detector import YOLODetector
from app.modules.evidence.evidence_generator import generate_evidence
from app.modules.violations.violation_engine import evaluate
from app.modules.violations.seve_engine import SEVE
from app.modules.ocr.paddle_ocr import PlateOCR
from app.services.mongo_service import MongoService
import time

detector = YOLODetector()
ocr_engine = PlateOCR()

def process_detection(image_path: str):
    start_time = time.time()
    
    # 1. Run Environment Quality Score (SEVE)
    eqs_result = SEVE.calculate_eqs(image_path)
    if eqs_result["status"] == "REJECTED":
        return {
            "status": "FAILED",
            "message": "Image quality too poor for automated enforcement.",
            "eqs": eqs_result
        }

    # 2. Run Object Detection (YOLO)
    detections = detector.detect(image_path)

    # 3. Extract and Validate License Plates (OCR + SEVE)
    extracted_plates = []
    for det in detections:
        if det["class_name"] == "license_plate":
            plate_info = ocr_engine.extract_and_validate(image_path, det["bbox"])
            det["ocr_data"] = plate_info  # Inject OCR data into detection record
            if plate_info["status"] == "VALIDATED":
                extracted_plates.append(plate_info["plate"])

    # 4. Evaluate Violations (SEVE Engine)
    violations = evaluate(detections)

    # 5. Generate Evidence Image with Bounding Boxes
    filename = os.path.basename(image_path)
    output_path = f"data/results/evidence_{filename}"
    # Pass the violations list into the generator
    generate_evidence(image_path, detections, violations, output_path)

    # 6. Save to MongoDB
    record_id = MongoService.save_detection(
        image_name=filename,
        detections=detections,
        violations=violations,
        evidence_path=output_path
    )

    processing_time = round(time.time() - start_time, 2)

    return {
        "status": "SUCCESS",
        "record_id": record_id,
        "processing_time_sec": processing_time,
        "environment_quality": eqs_result,
        "plates_detected": extracted_plates,
        "violations": violations,
        "evidence_url": output_path
    }