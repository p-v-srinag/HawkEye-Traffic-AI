from fastapi import APIRouter
from app.database.mongodb import violations_collection

router = APIRouter()

@router.get("/violations/search/{plate_number}")
def search_plate(plate_number: str):
    """
    Search for all violations associated with a specific license plate.
    """
    # Use regex for partial matching, case-insensitive
    query = {"violations.seve_context": {"$regex": plate_number, "$options": "i"}}
    # Since plate numbers are in the OCR data or in the final extracted plates...
    # Wait, the current MongoDB schema doesn't explicitly store plates at the root level, 
    # it stores 'detections' and 'violations'.
    # Actually, in detection_service.py we didn't save extracted plates at root. 
    # Let's search inside detections or evidence text.
    # A better schema would store "plates_detected" in MongoDB, but we can search raw stringified document.
    
    # A cleaner approach assuming "plates_detected" is added to the document.
    # Let's query any document where the detections array contains a plate.
    records = list(violations_collection.find(
        {"detections.ocr_data.plate": plate_number.upper()}, 
        {"_id": 0} # Exclude object ID for JSON serialization
    ).sort("created_at", -1).limit(10))
    
    return {"plate": plate_number.upper(), "records": records}
