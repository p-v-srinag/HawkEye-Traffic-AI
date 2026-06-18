from paddleocr import PaddleOCR


class PlateOCR:

    def __init__(self):

        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )

    def extract(self, image_path):

        result = self.ocr.ocr(
            image_path
        )

        return result