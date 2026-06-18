from datetime import datetime

from app.database.mongodb import (
    violations_collection
)


class MongoService:

    @staticmethod
    def save_detection(
        image_name,
        detections,
        violations,
        evidence_path
    ):

        document = {

            "image_name":
            image_name,

            "detections":
            detections,

            "violations":
            violations,

            "evidence_path":
            evidence_path,

            "created_at":
            datetime.utcnow()
        }

        result = (
            violations_collection
            .insert_one(document)
        )

        return str(
            result.inserted_id
        )