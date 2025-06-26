import os
import re
import tempfile
from google.cloud import vision
from google.cloud import language_v1
from human_detection import extract_person_names
from bank_name import analyze_entities

# Global clients (initialized once)
vision_client = None
nlp_client = None

def setup_google_vision_credentials():
    try:
        service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not service_account_info:
            raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON is not set!")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
            temp.write(service_account_info.encode())
            temp_path = temp.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
            return vision.ImageAnnotatorClient()
    except Exception as e:
        raise RuntimeError(f"Failed to set up Google Vision credentials: {e}")

def setup_google_nlp_client():
    try:
        return language_v1.LanguageServiceClient()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google NLP client: {e}")

# Initialize global clients once
vision_client = setup_google_vision_credentials()
nlp_client = setup_google_nlp_client()

# Regex patterns
card_number_pattern = r'\b(?:\d[ -]*?){13,16}\b'
expiry_date_pattern = r'\b\d{2}/\d{2}\b'
card_type_pattern = r'(?i)\b(?:VISA|Master\s*Card|MasterCard|Debit|Credit|American\s*Express|Discover|JCB|Diners\s*Club|Union\s*Pay)\b'

def extract_text_from_image(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = vision_client.text_detection(image=image)
        if response.error.message:
            raise Exception(f'API Error: {response.error.message}')
        return response.text_annotations[0].description if response.text_annotations else ""
    except Exception as e:
        raise RuntimeError(f"Text extraction failed: {e}")

def extract_info(text):
    """
    Uses global nlp_client inside this function.
    """
    global nlp_client
    try:
        return {
            'Card Number': re.findall(card_number_pattern, text),
            'Expiry Date': re.findall(expiry_date_pattern, text),
            'Bank Name': analyze_entities(text, nlp_client),  # Uses global nlp_client
            'Card Type': re.findall(card_type_pattern, text),
            'Card Holder Name': extract_person_names(text)
        }
    except Exception as e:
        raise RuntimeError(f"Failed to extract card info: {e}")

# Example test (if run standalone)
if __name__ == "__main__":
    image_path = './Bank-Cards-Reader/card2.png'
    try:
        text = extract_text_from_image(image_path)
        info = extract_info(text)
        print("\n=== OCR Output ===")
        print(text)
        print("\n=== Extracted Info ===")
        for key, value in info.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {str(e)}")
