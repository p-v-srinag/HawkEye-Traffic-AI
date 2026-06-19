from ultralytics import YOLO

class YOLODetector:
    def __init__(self):
        # We will use the nano model for speed during the hackathon demo
        self.model = YOLO("weights/yolo11n.pt")

    def detect(self, image_path):
        # CHANGED: We use .track() instead of calling the model directly to enable BoT-SORT
        results = self.model.track(
            image_path, 
            persist=True, 
            tracker="botsort.yaml",
            verbose=False # Keeps terminal clean
        )

        detections = []
        for r in results:
            names = r.names
            for box in r.boxes:
                cls_id = int(box.cls[0])
                
                # Extract tracking ID if it exists (crucial for Wrong Side Driving trajectory)
                track_id = int(box.id[0]) if box.id is not None else None

                detections.append({
                    "track_id": track_id,
                    "class_name": names[cls_id],
                    "confidence": float(box.conf[0]),
                    "bbox": box.xyxy[0].tolist()
                })

        return detections