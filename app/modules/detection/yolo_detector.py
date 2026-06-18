from ultralytics import YOLO


class YOLODetector:

    def __init__(self):

        self.model = YOLO(
            "weights/yolo11n.pt"
        )

    def detect(self, image_path):

        results = self.model(image_path)

        return results