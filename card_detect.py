import os
import json
import re
import tempfile
from google.cloud import vision
from human_detection import extract_person_names
from bank_name import analyze_entities

# Step 1: Read service account JSON from environment variable (Render)
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

# Step 2: Write to temp file for Google client to read
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON is not set!")

# Initialize Google Vision client
client = vision.ImageAnnotatorClient()

# ------------------ Regex Patterns ------------------
card_number_pattern = r'\b(?:\d[ -]*?){13,16}\b'
expiry_date_pattern = r'\b\d{2}/\d{2}\b'
card_type_pattern = r'(?i)\b(?:VISA|Master\s*Card|MasterCard|Debit|Credit|American\s*Express|Discover|JCB|Diners\s*Club|Union\s*Pay)\b'
card_holder_name_pattern = r'\b(?!valid\s*thru|good\s*thru)[A-Z]{2,}(?:\s[A-Z]{2,})*\b'
# (Bank names handled by `analyze_entities` using NLP)

# ------------------ OCR Function ------------------
def extract_text_from_image(image_path):
    """
    Uses Google Cloud Vision to extract text from an image.
    """
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f'API Error: {response.error.message}')

    return response.text_annotations[0].description if response.text_annotations else ""

# ------------------ Info Extraction ------------------
def extract_info(text):
    """
    Extracts card-related info from OCR'd text using regex + NLP.
    """
    info = {
        'Card Number': re.findall(card_number_pattern, text),
        'Expiry Date': re.findall(expiry_date_pattern, text),
        'Bank Name': analyze_entities(text),  # Uses NLP model
        'Card Type': re.findall(card_type_pattern, text),
        'Card Holder Name': extract_person_names(text)  # Custom logic
    }
    return info

# ------------------ Testing ------------------
if __name__ == "__main__":
    image_path = './Bank-Cards-Reader/card2.png'  # Example path
    try:
        text = extract_text_from_image(image_path)
        info = extract_info(text)

        print("=== OCR Output ===")
        print(text)
        print("\n=== Extracted Info ===")
        for k, v in info.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"Error during processing: {str(e)}")
