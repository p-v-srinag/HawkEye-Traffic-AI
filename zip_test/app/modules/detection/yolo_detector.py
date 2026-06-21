from ultralytics import YOLO

class YOLODetector:
    def __init__(self):
        # Upgrading to YOLO-World to support Zero-Shot Open Vocabulary Detection!
        # This natively supports finding helmets and seatbelts without custom datasets.
        self.model = YOLO("yolov8s-world.pt")
        self.model.set_classes(["helmet", "seatbelt", "person", "motorcycle", "car", "bus", "truck", "red traffic light", "green traffic light", "license plate"])

    def detect(self, image_path, is_sequence=False):
        # ALWAYS use .track() with botsort to satisfy the advanced tracking requirement
        # even for single frames, which provides a tracking ID natively
        results = self.model.track(
            image_path, 
            persist=True, 
            tracker="botsort.yaml",
            conf=0.05,
            iou=0.45,
            verbose=False
        )

        detections = []
        for r in results:
            names = r.names
            for box in r.boxes:
                cls_id = int(box.cls[0])
                class_name = names[cls_id]
                confidence = float(box.conf[0])
                
                # Apply custom confidence thresholds:
                # 0.05 for license plates (small objects)
                # 0.25 for persons (obscured passengers)
                # 0.45 for everything else (strict mode)
                if class_name == "license plate" and confidence < 0.05:
                    continue
                elif class_name == "person" and confidence < 0.25:
                    continue
                elif class_name not in ["person", "license plate"] and confidence < 0.45:
                    continue
                
                # Extract tracking ID if it exists
                track_id = int(box.id[0]) if getattr(box, 'id', None) is not None else None

                detections.append({
                    "track_id": track_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": box.xyxy[0].tolist()
                })

        return detections