import cv2
import numpy as np

class SEVE:
    """
    Smart Enforcement Validation Engine.
    Handles real-world edge cases to reduce false positives.
    """
    
    @staticmethod
    def calculate_eqs(image_path: str) -> dict:
        """
        Environment Quality Score (EQS) - Edge Case 8.
        Bengaluru has heavy rain and night glare. 
        If EQS < 40, we flag for manual review instead of auto-fining.
        """
        image = cv2.imread(image_path)
        if image is None:
            return {"score": 0, "status": "REJECTED", "reason": "Unreadable"}

        # Calculate Blur (Variance of Laplacian)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate Brightness
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])

        # Normalize scores (0-100)
        norm_blur = min(100, (blur_score / 500) * 100)
        norm_bright = 100 - abs(127 - brightness) # Peak score at perfect mid-tone (127)

        # EQS Formula
        eqs_score = int((norm_blur * 0.6) + (norm_bright * 0.4))

        if eqs_score < 40:
             return {"score": eqs_score, "status": "MANUAL_REVIEW", "reason": "Low Visibility / Blur"}
        return {"score": eqs_score, "status": "PROCEED", "reason": "Clear"}
    
    @staticmethod
    def validate_helmet_compliance(rider_bbox: list, helmet_bboxes: list) -> dict:
        """
        Edge Case 1: Helmet on Handlebar vs. Head.
        Calculates if the helmet is actually in the upper 30% (head region) of the rider's bounding box.
        """
        if not helmet_bboxes:
            return {"violation": True, "reason": "No helmet detected in frame"}

        rx1, ry1, rx2, ry2 = rider_bbox
        rider_height = ry2 - ry1
        
        # Define the "Head Region" (top 30% of the rider's bounding box)
        head_region_max_y = ry1 + (rider_height * 0.30)

        for helmet in helmet_bboxes:
            hx1, hy1, hx2, hy2 = helmet
            helmet_center_y = hy1 + ((hy2 - hy1) / 2)

            # Check if helmet is roughly within the horizontal bounds of THIS rider
            # AND if the helmet's center sits in the upper 30% of the body
            if (hx1 >= rx1 - 40 and hx2 <= rx2 + 40) and (helmet_center_y <= head_region_max_y):
                return {"violation": False, "reason": "Helmet correctly worn on head"}

        return {"violation": True, "reason": "Helmet detected but not worn on head (likely on handlebar)"}
    
    @staticmethod
    def validate_red_light_violation(vehicle_bboxes: list, traffic_lights: list, frame_height: int) -> list:
        """
        Edge Case 5: Red Light & Stop-Line Validation.
        Only penalize if the light is RED and the vehicle centroid has crossed into the lower 40% of the frame (Stop-Line Zone).
        """
        violating_vehicles = []
        is_red_light = False

        for light in traffic_lights:
            if light["class_name"] == "red traffic light":
                is_red_light = True
                break

        if not is_red_light:
            return violating_vehicles # No violation if light is green or yellow

        # Define Stop Line Zone (e.g., bottom 40% of the image)
        stop_line_y_threshold = frame_height * 0.60 

        for vehicle in vehicle_bboxes:
            vx1, vy1, vx2, vy2 = vehicle["bbox"]
            vehicle_bottom_y = vy2 # The bottom tire edge of the vehicle

            if vehicle_bottom_y > stop_line_y_threshold:
                violating_vehicles.append({
                    "bbox": vehicle["bbox"],
                    "confidence": vehicle["confidence"],
                    "reason": "Crossed stop line during active red light"
                })

        return violating_vehicles
    
    @staticmethod
    def validate_triple_riding(persons_bboxes: list) -> dict:
        """
        Edge Case 2: Child Passenger vs. Triple Riding.
        Bengaluru police don't heavily penalize a husband, wife, and a small child.
        """
        if len(persons_bboxes) < 3:
            return {"violation": False, "reason": "Less than 3 riders"}
            
        areas = []
        for box in persons_bboxes:
            # box format: [x1, y1, x2, y2]
            width = box[2] - box[0]
            height = box[3] - box[1]
            areas.append(width * height)
            
        areas.sort(reverse=True)
        
        largest_rider_area = areas[0]
        smallest_rider_area = areas[-1]
        
        # Calculate size ratio
        child_ratio = smallest_rider_area / largest_rider_area
        
        # If the smallest person is 55% smaller than the largest (ratio < 0.55), it's a child.
        if child_ratio < 0.55:
            return {
                "violation": False, 
                "riders": len(persons_bboxes), 
                "reason": "Child passenger detected (suppressing violation)"
            }
            
        return {
            "violation": True, 
            "riders": len(persons_bboxes), 
            "reason": "3+ Adult riders detected"
        }

    @staticmethod
    def validate_wrong_side_driving(trajectory: dict, expected_dy_positive: bool = True) -> dict:
        """
        Edge Case 3: Wrong Side Driving using Evidence Burst Trajectory.
        Assuming lane traffic should be moving 'down' the image (dy > 0).
        If vehicle moves 'up' significantly (dy < -20), flag as wrong side.
        """
        if trajectory["is_stationary"]:
            return {"violation": False, "reason": "Vehicle stationary"}
            
        dx, dy = trajectory["direction"]
        
        # If expected direction is down (dy > 0), and vehicle moves up (dy < -20)
        if expected_dy_positive and dy < -20:
            return {"violation": True, "reason": "Moving against lane direction (opposite vector detected)"}
        elif not expected_dy_positive and dy > 20:
            return {"violation": True, "reason": "Moving against lane direction (opposite vector detected)"}
            
        return {"violation": False, "reason": "Moving with traffic flow"}

    @staticmethod
    def validate_overspeeding(trajectory: dict, speed_limit_px: int = 50) -> dict:
        """
        Bonus Feature: Overspeeding using Trajectory Vector Magnitude.
        Calculates the pixel displacement per frame across the Evidence Burst.
        If it exceeds the pixel-speed limit, flag as overspeeding.
        """
        if trajectory["is_stationary"]:
            return {"violation": False, "reason": "Vehicle stationary"}
            
        dx, dy = trajectory["direction"]
        pixel_velocity = (dx**2 + dy**2)**0.5
        
        if pixel_velocity > speed_limit_px:
             return {"violation": True, "reason": f"Excessive pixel velocity ({int(pixel_velocity)}px/frame > {speed_limit_px})"}
             
        return {"violation": False, "reason": "Within safe velocity limits"}

    @staticmethod
    def validate_illegal_parking(trajectory: dict, bbox: list, frame_height: int, frame_width: int) -> dict:
        """
        Edge Case 4: Illegal Parking using Evidence Burst Trajectory.
        If stationary > threshold AND inside No-Parking Zone.
        Assuming left-most 20% of the screen is No-Parking shoulder zone.
        """
        x1, y1, x2, y2 = bbox
        centroid_x = (x1 + x2) / 2.0
        
        # Define No-Parking Zone (e.g., left 20% of image width)
        in_no_parking_zone = centroid_x < (frame_width * 0.20)
        
        if in_no_parking_zone and trajectory["is_stationary"]:
            return {"violation": True, "reason": "Stationary vehicle detected in No-Parking zone across burst"}
            
        return {"violation": False, "reason": "Vehicle is moving or outside restricted zone"}

    @staticmethod
    def validate_seatbelt_compliance(driver_bbox: list, seatbelt_bboxes: list, eqs_score: int) -> dict:
        """
        Edge Case 6: Seatbelt Detection. Night/Glare/Tinted glass.
        Three-state output: Seatbelt, No Seatbelt, Undetermined.
        """
        if eqs_score < 40:
             return {"violation": False, "reason": "UNDETERMINED - Image quality insufficient for seatbelt check"}
             
        # Check if any seatbelt is within the driver's bounding box
        dx1, dy1, dx2, dy2 = driver_bbox
        for belt in seatbelt_bboxes:
            bx1, by1, bx2, by2 = belt
            
            # Simple intersection check
            if not (bx2 < dx1 or bx1 > dx2 or by2 < dy1 or by1 > dy2):
                return {"violation": False, "reason": "Seatbelt detected securely"}
                
        # If quality is good, and no seatbelt intersects driver
        return {"violation": True, "reason": "Seatbelt NOT detected on driver"}