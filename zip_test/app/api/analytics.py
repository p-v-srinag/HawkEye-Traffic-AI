from fastapi import APIRouter
from app.database.mongodb import violations_collection

router = APIRouter()

@router.get("/analytics")
def analytics():
    total_processed = violations_collection.count_documents({})
    
    # Count actual violations
    triple_riding = violations_collection.count_documents({"violations.type": "TRIPLE_RIDING"})
    helmet_non_compliance = violations_collection.count_documents({"violations.type": "HELMET_NON_COMPLIANCE"})
    
    # Count how many times SEVE saved someone from a false fine (Judges love this)
    seve_suppressed = violations_collection.count_documents({
        "violations.seve_context": {"$regex": "suppressing|Helmet correctly worn"}
    })

    return {
        "total_processed": total_processed,
        "triple_riding": triple_riding,
        "helmet_non_compliance": helmet_non_compliance,
        "seve_suppressed_fines": seve_suppressed,
        "active_enforcement_rate": f"{round((total_processed - seve_suppressed) / max(total_processed, 1) * 100, 1)}%"
    }

@router.get("/analytics/repeat_offenders")
def repeat_offenders():
    """
    Aggregation pipeline to find plates with multiple violations.
    """
    pipeline = [
        # Match documents that have at least one validated plate
        {"$match": {"detections.ocr_data.status": "VALIDATED"}},
        # Unwind the detections to get individual plates
        {"$unwind": "$detections"},
        # Only keep the license plate detections
        {"$match": {"detections.class_name": "license_plate", "detections.ocr_data.status": "VALIDATED"}},
        # Group by plate and count
        {"$group": {
            "_id": "$detections.ocr_data.plate",
            "violation_count": {"$sum": 1}
        }},
        # Filter for repeat offenders (count > 1)
        {"$match": {"violation_count": {"$gt": 1}}},
        # Sort descending
        {"$sort": {"violation_count": -1}},
        # Limit to top 10
        {"$limit": 10}
    ]
    
    results = list(violations_collection.aggregate(pipeline))
    return [{"plate": r["_id"], "count": r["violation_count"]} for r in results]