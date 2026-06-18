from ultralytics import YOLO


class YOLODetector:

    def __init__(self):

        self.model = YOLO(
            "weights/yolo11n.pt"
        )

    def detect(self, image_path):

        results = self.model(
            image_path
        )

        detections = []

        for r in results:

            names = r.names

            for box in r.boxes:

                cls_id = int(box.cls[0])

                detections.append(
                    {
                        "class_name":
                        names[cls_id],

                        "confidence":
                        float(box.conf[0]),

                        "bbox":
                        box.xyxy[0].tolist()
                    }
                )

        return detections