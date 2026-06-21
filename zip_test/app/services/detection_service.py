import os
from app.modules.detection.yolo_detector import YOLODetector
from app.modules.evidence.evidence_generator import generate_evidence
from app.modules.violations.violation_engine import evaluate
from app.modules.violations.seve_engine import SEVE
from app.modules.preprocessing.enhancer import ImageEnhancer
from app.modules.ocr.paddle_ocr import PlateOCR
from app.services.mongo_service import MongoService
import time

detector = YOLODetector()
ocr_engine = PlateOCR()

def process_detection(image_path: str):
    start_time = time.time()
    
    # 0. Advanced Image Preprocessing (Low Light, Motion Blur)
    enhanced_image_path = ImageEnhancer.process(image_path)
    
    # 1. Run Environment Quality Score (SEVE) on original image to log quality, but use enhanced for detection
    eqs_result = SEVE.calculate_eqs(image_path)
    if eqs_result["status"] == "REJECTED":
        return {
            "status": "FAILED",
            "message": "Image quality too poor for automated enforcement.",
            "eqs": eqs_result
        }

    # 2. Run Object Detection (YOLO) on Enhanced Image
    detections = detector.detect(enhanced_image_path)

    # 3. Extract and Validate License Plates (OCR + SEVE)
    extracted_plates = []
    vehicles = [d for d in detections if d["class_name"] in ["car", "motorcycle", "bus", "truck"]]
    native_plates = [d for d in detections if d["class_name"] == "license plate"]
    
    for vehicle in vehicles:
        mx1, my1, mx2, my2 = vehicle["bbox"]
        
        # Check if YOLO natively detected a license plate on this vehicle
        plate_bbox = None
        matched_native_plate = None
        for plate in native_plates:
            px1, py1, px2, py2 = plate["bbox"]
            # Intersection check
            if not (px2 < mx1 or px1 > mx2 or py2 < my1 or py1 > my2):
                plate_bbox = plate["bbox"]
                matched_native_plate = plate
                break
                
        # Fallback to full vehicle crop ONLY if YOLO completely missed it
        if plate_bbox is None:
            plate_bbox = [mx1, my1, mx2, my2]
        
        # Pass the highly-accurate bounding box into PaddleOCR
        plate_info = ocr_engine.extract_and_validate(enhanced_image_path, plate_bbox)
        
        if plate_info["status"] in ["VALIDATED", "SUSPICIOUS", "MANUAL_REVIEW"]:
            extracted_plates.append(plate_info["plate"])
            
            if matched_native_plate:
                # Enrich the existing YOLO detection with OCR data
                matched_native_plate["ocr_data"] = plate_info
                matched_native_plate["confidence"] = max(matched_native_plate["confidence"], 0.85)
            else:
                # Inject a synthetic license plate detection if we used a fallback crop
                detections.append({
                    "track_id": vehicle.get("track_id"),
                    "class_name": "license plate",
                    "confidence": 0.85 if plate_info["status"] == "VALIDATED" else 0.50,
                    "bbox": plate_bbox,
                    "ocr_data": plate_info
                })


    # 4. Evaluate Violations (SEVE Engine)
    violations = evaluate(detections)

    # 5. Generate Evidence Image with Bounding Boxes
    filename = os.path.basename(image_path)
    output_path = f"data/results/evidence_{filename}"
    # Pass the violations list into the generator
    generate_evidence(enhanced_image_path, detections, violations, output_path)

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

from app.modules.tracking.bot_sort_tracker import BurstTracker

def process_burst_detection(image_paths: list):
    """
    Processes an Evidence Burst (multiple images) to establish temporal trajectories.
    Allows detection of Wrong Side Driving and Illegal Parking from a photo burst.
    """
    start_time = time.time()
    tracker = BurstTracker()
    
    all_detections = []
    final_violations = []
    extracted_plates = set()
    eqs_result = None
    
    # Process sequentially to build tracks
    for idx, img_path in enumerate(image_paths):
        # Enhance
        enhanced_path = ImageEnhancer.process(img_path)
        
        # We only really care about EQS of the primary/first frame for simplicity
        if idx == 0:
            eqs_result = SEVE.calculate_eqs(img_path)
            
        # Detect
        detections = detector.detect(enhanced_path, is_sequence=True)
        all_detections.append((enhanced_path, detections))
        
        # Update Tracks
        tracker.update(detections, idx)
        
        # OCR: Use PaddleOCR on all vehicles to find license plates natively
        vehicles = [d for d in detections if d["class_name"] in ["car", "motorcycle", "bus", "truck"]]
        native_plates = [d for d in detections if d["class_name"] == "license plate"]
        
        for vehicle in vehicles:
            mx1, my1, mx2, my2 = vehicle["bbox"]
            
            # Check if YOLO natively detected a license plate on this vehicle
            plate_bbox = None
            matched_native_plate = None
            for plate in native_plates:
                px1, py1, px2, py2 = plate["bbox"]
                if not (px2 < mx1 or px1 > mx2 or py2 < my1 or py1 > my2):
                    plate_bbox = plate["bbox"]
                    matched_native_plate = plate
                    break
            
            # Fallback to full vehicle crop ONLY if YOLO completely missed it
            if plate_bbox is None:
                plate_bbox = [mx1, my1, mx2, my2]
            
            plate_info = ocr_engine.extract_and_validate(enhanced_path, plate_bbox)
            
            if plate_info["status"] in ["VALIDATED", "SUSPICIOUS", "MANUAL_REVIEW"]:
                extracted_plates.add(plate_info["plate"])
                
                if matched_native_plate:
                    # Enrich the existing YOLO detection with OCR data
                    matched_native_plate["ocr_data"] = plate_info
                    matched_native_plate["confidence"] = max(matched_native_plate["confidence"], 0.85)
                else:
                    # Inject a synthetic license plate detection
                    detections.append({
                        "track_id": vehicle.get("track_id"),
                        "class_name": "license plate",
                        "confidence": 0.85 if plate_info["status"] == "VALIDATED" else 0.50,
                        "bbox": plate_bbox,
                        "ocr_data": plate_info
                    })

    # Analyze trajectories
    trajectories = {}
    for track_id in tracker.tracks.keys():
        trajectories[track_id] = tracker.get_trajectory_analysis(track_id)
        
    # Evaluate violations on the LAST frame using all accumulated trajectories
    last_enhanced_path, last_detections = all_detections[-1]
    
    final_violations = evaluate(
        last_detections, 
        image_path=last_enhanced_path, 
        eqs_score=eqs_result["score"] if eqs_result else 100, 
        trajectories=trajectories
    )
    
    # Generate Evidence on the last frame
    filename = os.path.basename(last_enhanced_path)
    output_path = f"data/results/evidence_burst_{filename}"
    generate_evidence(last_enhanced_path, last_detections, final_violations, output_path)
    
    # Save to MongoDB
    record_id = MongoService.save_detection(
        image_name=f"burst_{filename}",
        detections=last_detections,
        violations=final_violations,
        evidence_path=output_path
    )
    
    return {
        "status": "SUCCESS",
        "record_id": record_id,
        "processing_time_sec": round(time.time() - start_time, 2),
        "environment_quality": eqs_result,
        "plates_detected": list(extracted_plates),
        "violations": final_violations,
        "evidence_url": output_path,
        "burst_frames": len(image_paths)
    }