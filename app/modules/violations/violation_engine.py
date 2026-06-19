from app.modules.violations.seve_engine import SEVE
import cv2

def evaluate(detections: list, image_path: str = None) -> list:
    violations = []
    
    # 1. Separate detections into categories
    motorcycles = [d for d in detections if d["class_name"] == "motorcycle"]
    persons = [d for d in detections if d["class_name"] == "person"]
    helmets = [d for d in detections if d["class_name"] == "helmet"]
    traffic_lights = [d for d in detections if "traffic_light" in d["class_name"]]
    
    # Get frame dimensions for spatial rules
    frame_height = 1080 # Default
    if image_path:
        img = cv2.imread(image_path)
        if img is not None:
            frame_height, _, _ = img.shape

    # 2. Evaluate Triple Riding using SEVE (Child passenger logic)
    if motorcycles and len(persons) >= 3:
        person_bboxes = [p["bbox"] for p in persons]
        triple_riding_check = SEVE.validate_triple_riding(person_bboxes)
        
        if triple_riding_check["violation"]:
            violations.append({
                "type": "TRIPLE_RIDING",
                "confidence": 0.92,
                "riders": triple_riding_check["riders"],
                "seve_context": triple_riding_check["reason"]
            })

    # 3. Evaluate Helmet Compliance using SEVE (Spatial checking)
    if motorcycles and persons:
        helmet_bboxes = [h["bbox"] for h in helmets]
        for person in persons:
            helmet_check = SEVE.validate_helmet_compliance(person["bbox"], helmet_bboxes)
            if helmet_check["violation"]:
                violations.append({
                    "type": "HELMET_NON_COMPLIANCE",
                    "confidence": person["confidence"],
                    "seve_context": helmet_check["reason"]
                })

    # 4. Evaluate Red Light / Stop Line
    if traffic_lights and motorcycles:
        red_light_violators = SEVE.validate_red_light_violation(motorcycles, traffic_lights, frame_height)
        for violator in red_light_violators:
            violations.append({
                "type": "RED_LIGHT_VIOLATION",
                "confidence": violator["confidence"],
                "seve_context": violator["reason"]
            })

    return violations