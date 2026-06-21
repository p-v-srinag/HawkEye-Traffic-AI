import re

# We use a highly tolerant regex to find the plate substring inside messy OCR text.
# Indian plates: 2 letters, 1-2 numbers, 1-2 letters, 4 numbers.
# OCR often confuses: 0/O, 1/I, 5/S, 8/B, 2/Z.
# So we allow these substitutions in the regex.
STATE_CODE = r"[A-Z0-9]{2}" # E.g., CH, MH, KA
RTO_CODE = r"[0-9OIZSB]{1,2}" # E.g., 01, O1
LETTERS = r"[A-Z0-9]{1,2}" # E.g., AH
NUMBERS = r"[0-9OIZSB]{3,4}" # E.g., 2488

# Combines to find the 8-10 char pattern anywhere in the string
TOLERANT_REGEX = f"({STATE_CODE}{RTO_CODE}{LETTERS}{NUMBERS})"

def correct_characters(plate_text: str) -> str:
    """
    Applies positional corrections ONLY to a relatively clean plate string.
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
        if corrected[i] == 'Z': corrected[i] = '2'

    # Last 4 chars MUST be numbers
    for i in range(max(4, len(corrected)-4), len(corrected)):
        if corrected[i] == 'O': corrected[i] = '0'
        if corrected[i] == 'I': corrected[i] = '1'
        if corrected[i] == 'B': corrected[i] = '8'
        if corrected[i] == 'S': corrected[i] = '5'
        if corrected[i] == 'Z': corrected[i] = '2'
            
    return "".join(corrected)

def validate_plate(raw_text: str):
    cleaned = raw_text.upper().replace(" ", "").replace("-", "")
    
    # Extract using tolerant regex
    match = re.search(TOLERANT_REGEX, cleaned)
    if match:
        plate = correct_characters(match.group(1))
        # After correction, does it look like a perfect plate?
        perfect_regex = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$"
        if re.match(perfect_regex, plate):
            return {"status": "VALIDATED", "plate": plate}
        else:
            return {"status": "SUSPICIOUS", "plate": plate}
            
    # If even tolerant regex fails, maybe it's just 8-10 chars long?
    if 8 <= len(cleaned) <= 10:
        plate = correct_characters(cleaned)
        return {"status": "SUSPICIOUS", "plate": plate}
        
    return {"status": "MANUAL_REVIEW", "plate": cleaned}