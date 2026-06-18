import os

from app.modules.detection.yolo_detector import (
    YOLODetector
)

from app.modules.evidence.evidence_generator import (
    generate_evidence
)
from app.modules.violations.violation_engine import (
    evaluate
)
from app.services.mongo_service import (
    MongoService
)
detector = YOLODetector()


def process_detection(
    image_path
):

    detections = detector.detect(
        image_path
    )

    violations = evaluate(
        detections
    )
    record_id = (
        MongoService.save_detection(
            image_path,
            detections,
            violations,
            output_path
        )
    )
    filename = os.path.basename(
        image_path
    )

    output_path = (
        f"data/results/{filename}"
    )

    generate_evidence(
        image_path,
        detections,
        output_path
    )

    return {

        "record_id":
        record_id,

        "detections":
        detections,

        "violations":
        violations,

        "evidence":
        output_path
    }