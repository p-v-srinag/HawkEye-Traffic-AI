import re

# Standard Indian License Plate Format: KA01AB1234
PLATE_REGEX = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$"

def correct_characters(plate_text: str) -> str:
    """
    Applies positional corrections to common OCR mistakes.
    Essential for Edge Case 7 (OCR Rectification).
    """
    plate_text = plate_text.upper().replace(" ", "").replace("-", "")
    
    if len(plate_text) < 8 or len(plate_text) > 10:
        return plate_text
        
    corrected = list(plate_text)
    
    # First 2 chars MUST be letters (State Code)
    for i in range(min(2, len(corrected))):
        if corrected[i] == '0': corrected[i] = 'O'
        if corrected[i] == '1': corrected[i] = 'I'
        if corrected[i] == '8': corrected[i] = 'B'
        if corrected[i] == '5': corrected[i] = 'S'
            
    # Next 2 chars MUST be numbers (RTO Code)
    for i in range(2, min(4, len(corrected))):
        if corrected[i] == 'O': corrected[i] = '0'
        if corrected[i] == 'I': corrected[i] = '1'
        if corrected[i] == 'B': corrected[i] = '8'
        if corrected[i] == 'S': corrected[i] = '5'
        if corrected[i] == 'G': corrected[i] = '6'

    # Last 4 chars MUST be numbers
    for i in range(max(4, len(corrected)-4), len(corrected)):
        if corrected[i] == 'O': corrected[i] = '0'
        if corrected[i] == 'I': corrected[i] = '1'
        if corrected[i] == 'B': corrected[i] = '8'
        if corrected[i] == 'S': corrected[i] = '5'
        if corrected[i] == 'G': corrected[i] = '6'
            
    return "".join(corrected)

def validate_plate(plate_text: str):
    """
    Evaluates the plate against standard formats to detect fakes/errors.
    Addresses Edge Case 9.
    """
    cleaned = correct_characters(plate_text)
    
    if re.match(PLATE_REGEX, cleaned):
        return {"status": "VALIDATED", "plate": cleaned}
    elif 8 <= len(cleaned) <= 10:
        return {"status": "SUSPICIOUS", "plate": cleaned}
    else:
        return {"status": "MANUAL_REVIEW", "plate": cleaned}