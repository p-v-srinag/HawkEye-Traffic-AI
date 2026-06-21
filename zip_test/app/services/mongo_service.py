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

        # Bonus Feature: Dynamic Financial Penalties (End-to-End Business Logic)
        # If any of the validated plates in this detection already exist in the DB, it's a repeat offender!
        is_repeat_offender = False
        plates_in_frame = [d.get("ocr_data", {}).get("plate") for d in detections if d.get("ocr_data", {}).get("status") == "VALIDATED"]
        
        for plate in plates_in_frame:
            if plate and violations_collection.count_documents({"detections.ocr_data.plate": plate}) > 0:
                is_repeat_offender = True
                break

        # Calculate dynamic fines
        total_challan_amount = 0
        for v in violations:
            base_fine = 500 # Default fine
            if v["type"] == "TRIPLE_RIDING": base_fine = 1000
            if v["type"] == "OVERSPEEDING": base_fine = 2000
            
            # Apply 2x penalty multiplier for repeat offenders
            v["fine_amount_inr"] = base_fine * 2 if is_repeat_offender else base_fine
            v["is_repeat_offender_penalty_applied"] = is_repeat_offender
            total_challan_amount += v["fine_amount_inr"]

        document = {
            "image_name": image_name,
            "detections": detections,
            "violations": violations,
            "evidence_path": evidence_path,
            "financials": {
                "total_challan_amount_inr": total_challan_amount,
                "repeat_offender_multiplier": 2.0 if is_repeat_offender else 1.0
            },
            "created_at": datetime.utcnow()
        }

        result = (
            violations_collection
            .insert_one(document)
        )

        return str(
            result.inserted_id
        )