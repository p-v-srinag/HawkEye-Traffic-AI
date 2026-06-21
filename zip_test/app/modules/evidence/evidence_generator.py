import cv2

def generate_evidence(image_path: str, detections: list, violations: list, output_path: str):
    """
    Generates the final visual evidence for the dashboard and database.
    Draws compliant objects in GREEN and violations in RED, attaching SEVE context.
    """
    image = cv2.imread(image_path)
    if image is None:
        return output_path

    # Extract violation types to color-code the boxes
    violation_types = [v["type"] for v in violations]
    is_triple_riding = "TRIPLE_RIDING" in violation_types

    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        cls_name = det["class_name"]
        
        # Default to Green (Compliant)
        color = (0, 255, 0)
        label = f"{cls_name} {det['confidence']:.2f}"

        # Logic to highlight violators in RED
        if is_triple_riding and cls_name in ["person", "motorcycle"]:
            color = (0, 0, 255) # Red in BGR
            
        if cls_name == "license plate" and "ocr_data" in det:
            ocr = det["ocr_data"]
            if ocr["status"] == "VALIDATED":
                label = f"PLATE: {ocr['plate']}"
                color = (255, 165, 0) # Orange for plates
            else:
                label = f"REVIEW: {ocr['plate']}"
                color = (0, 0, 255) # Red for suspicious plates

        # Draw Bounding Box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Draw Label Background (for readability against bright roads)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(image, (x1, y1 - 20), (x1 + tw, y1), color, -1)
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # Print SEVE Summary Banner at the top of the image
    if violations:
        y_offset = 30
        for v in violations:
            fine_text = f" (FINE: Rs. {v.get('fine_amount_inr', 'N/A')})" if "fine_amount_inr" in v else ""
            text = f"VIOLATION: {v['type']}{fine_text} | SEVE: {v.get('seve_context', '')}"
            
            # Draw a solid white background rectangle for readability
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(image, (20, y_offset - th - 5), (20 + tw, y_offset + 5), (255, 255, 255), -1)
            
            cv2.putText(image, text, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            y_offset += 35
    else:
        cv2.putText(image, "SEVE STATUS: COMPLIANT (No Actionable Violations)", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imwrite(output_path, image)
    return output_path