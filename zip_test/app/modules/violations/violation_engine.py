from app.modules.violations.seve_engine import SEVE
import cv2

def evaluate(detections: list, image_path: str = None, eqs_score: int = 100, trajectories: dict = None) -> list:
    violations = []
    
    # 1. Separate detections into categories
    motorcycles = [d for d in detections if d["class_name"] == "motorcycle"]
    cars = [d for d in detections if d["class_name"] == "car"]
    persons = [d for d in detections if d["class_name"] == "person"]
    helmets = [d for d in detections if d["class_name"] == "helmet"]
    seatbelts = [d for d in detections if d["class_name"] == "seatbelt"]
    traffic_lights = [d for d in detections if "traffic light" in d["class_name"]]
    
    # Get frame dimensions for spatial rules
    frame_height = 1080 # Default
    frame_width = 1920
    if image_path:
        img = cv2.imread(image_path)
        if img is not None:
            frame_height, frame_width, _ = img.shape

    def _boxes_intersect(boxA, boxB):
        # A simple intersection check between two bounding boxes [x1, y1, x2, y2]
        return not (boxA[2] < boxB[0] or boxA[0] > boxB[2] or boxA[3] < boxB[1] or boxA[1] > boxB[3])

    # 2 & 3. Evaluate Triple Riding & Helmet Compliance per Motorcycle
    if motorcycles and persons:
        helmet_bboxes = [h["bbox"] for h in helmets]
        
        for moto in motorcycles:
            # Find persons riding THIS motorcycle
            riders = [p for p in persons if _boxes_intersect(p["bbox"], moto["bbox"])]
            
            # Evaluate Triple Riding
            if len(riders) >= 3:
                rider_bboxes = [r["bbox"] for r in riders]
                triple_riding_check = SEVE.validate_triple_riding(rider_bboxes)
                if triple_riding_check["violation"]:
                    violations.append({
                        "type": "TRIPLE_RIDING",
                        "confidence": 0.92,
                        "riders": triple_riding_check["riders"],
                        "seve_context": triple_riding_check["reason"]
                    })
                    
            # Evaluate Helmet Compliance
            # Re-enabled! YOLO-World natively detects helmets.
            for rider in riders:
                helmet_check = SEVE.validate_helmet_compliance(rider["bbox"], helmet_bboxes)
                if helmet_check["violation"]:
                    violations.append({
                        "type": "HELMET_NON_COMPLIANCE",
                        "confidence": rider["confidence"],
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

    # 5. Evaluate Seatbelt Compliance (Edge Case 6)
    if cars and persons:
        seatbelt_bboxes = [s["bbox"] for s in seatbelts]
        for person in persons:
            # We assume a person in a car region is a driver
            seatbelt_check = SEVE.validate_seatbelt_compliance(person["bbox"], seatbelt_bboxes, eqs_score)
            if seatbelt_check["violation"]:
                violations.append({
                    "type": "SEATBELT_NON_COMPLIANCE",
                    "confidence": person["confidence"],
                    "seve_context": seatbelt_check["reason"]
                })
                
    # 6. Evaluate Trajectory Based Violations (Wrong Side & Illegal Parking)
    if trajectories:
        all_vehicles = motorcycles + cars
        for vehicle in all_vehicles:
            track_id = vehicle.get("track_id")
            if track_id is not None and track_id in trajectories:
                traj = trajectories[track_id]
                
                # Check Wrong Side Driving
                wsd_check = SEVE.validate_wrong_side_driving(traj, expected_dy_positive=True)
                if wsd_check["violation"]:
                    violations.append({
                        "type": "WRONG_SIDE_DRIVING",
                        "confidence": vehicle["confidence"],
                        "seve_context": wsd_check["reason"]
                    })
                    
                # Check Illegal Parking
                park_check = SEVE.validate_illegal_parking(traj, vehicle["bbox"], frame_height, frame_width)
                if park_check["violation"]:
                    violations.append({
                        "type": "ILLEGAL_PARKING",
                        "confidence": vehicle["confidence"],
                        "seve_context": park_check["reason"]
                    })
                    
                # Check Overspeeding
                speed_check = SEVE.validate_overspeeding(traj, speed_limit_px=80)
                if speed_check["violation"]:
                    violations.append({
                        "type": "OVERSPEEDING",
                        "confidence": vehicle["confidence"],
                        "seve_context": speed_check["reason"]
                    })

    return violations