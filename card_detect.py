import os
import re
import tempfile
from google.cloud import vision
from google.cloud import language_v1
from human_detection import extract_person_names
from bank_name import analyze_entities

# ------------------ Regex Patterns ------------------

card_number_pattern = r'\b(?:\d[ -]*?){13,16}\b'
expiry_date_pattern = r'\b\d{2}/\d{2}\b'
card_type_pattern = r'(?i)\b(?:VISA|Master\s*Card|MasterCard|Debit|Credit|American\s*Express|Discover|JCB|Diners\s*Club|Union\s*Pay)\b'
card_holder_name_pattern = r'\b(?!valid\s*thru|good\s*thru)[A-Z]{2,}(?:\s[A-Z]{2,})*\b'

# ------------------ Credential Setup ------------------

def setup_google_vision_client():
    """
    Sets up Google Vision API client using service account credentials from an environment variable.
    """
    try:
        credentials_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not credentials_json:
            raise EnvironmentError("❌ GOOGLE_SERVICE_ACCOUNT_JSON not set!")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(credentials_json.encode())
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file.name

        return vision.ImageAnnotatorClient()
    except Exception as e:
        raise RuntimeError(f"❌ Vision client setup failed: {e}")

def setup_google_nlp_client():
    """
    Initializes Google Cloud NLP client.
    """
    try:
        return language_v1.LanguageServiceClient()
    except Exception as e:
        raise RuntimeError(f"❌ NLP client setup failed: {e}")

# ------------------ OCR Function ------------------

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if response.error.message:
        raise Exception(f'{response.error.message}')
    return texts[0].description if texts else ""


# ------------------ Info Extraction ------------------

def extract_info(text):
    info = {}

    # Extracting information
    info['Card Number'] = re.findall(card_number_pattern, text)
    info['Expiry Date'] = re.findall(expiry_date_pattern, text)
    # info['Bank Name'] = re.findall(bank_name_pattern, text)
    nlp_client = language_v1.LanguageServiceClient()
    info['Bank Name'] = analyze_entities(text,nlp_client)
    
    info['Card Type'] = re.findall(card_type_pattern, text)
    info['Card Holder Name'] =extract_person_names(text) 

    return info

# ------------------ Main Test ------------------

# if __name__ == "__main__":
#     image_path = "./Bank-Cards-Reader/card2.png"  # Test path

#     try:
#         print("🔐 Setting up credentials...")
#         vision_client = setup_google_vision_client()
#         nlp_client = setup_google_nlp_client()

#         print("📸 Performing OCR...")
#         text = extract_text_from_image(image_path, vision_client)

#         print("🧾 Extracting card info...")
#         info = extract_info(text, nlp_client)

#         print("\n📝 OCR Text:\n", text)
#         print("\n✅ Extracted Info:")
#         for k, v in info.items():
#             print(f"{k}: {v}")

#     except Exception as e:
#         print(f"\n❌ Processing failed: {str(e)}")
