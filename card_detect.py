import reAdd commentMore actions
import tempfile
from google.cloud import vision
from google.cloud import language_v1
from human_detection import extract_person_names
from bank_name import analyze_entities

@@ -23,10 +24,17 @@
            temp_path = temp.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
            return vision.ImageAnnotatorClient()

    except Exception as e:
        raise RuntimeError(f"Failed to set up Google Vision credentials: {e}")

# ------------------ Setup Google NLP Client ------------------

def setup_google_nlp_client():
    try:
        return language_v1.LanguageServiceClient()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google NLP client: {e}")

# ------------------ Regex Patterns ------------------

card_number_pattern = r'\b(?:\d[ -]*?){13,16}\b'
@@ -36,7 +44,7 @@

# ------------------ OCR Function ------------------

def extract_text_from_image(image_path, client):
def extract_text_from_image(image_path, vision_client):
    """
    Uses Google Cloud Vision to extract text from an image.
    """
@@ -45,7 +53,7 @@
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        response = vision_client.text_detection(image=image)

        if response.error.message:
            raise Exception(f'API Error: {response.error.message}')
@@ -56,15 +64,15 @@

# ------------------ Info Extraction ------------------

def extract_info(text):
def extract_info(text, nlp_client):
    """
    Extracts card-related info from OCR'd text using regex + NLP.
    """
    try:
        return {
            'Card Number': re.findall(card_number_pattern, text),
            'Expiry Date': re.findall(expiry_date_pattern, text),
            'Bank Name': analyze_entities(text),  # NLP model for bank detection
            'Bank Name': analyze_entities(text, nlp_client),  # ✅ Fix: passed required client
            'Card Type': re.findall(card_type_pattern, text),
            'Card Holder Name': extract_person_names(text)  # Custom logic
        }
@@ -74,24 +82,25 @@
# ------------------ Testing ------------------

if __name__ == "__main__":
    image_path = './Bank-Cards-Reader/card2.png'  # Example test image
    image_path = './Bank-Cards-Reader/card2.png'  # Update to actual path

    try:
        print("Setting up credentials...")
        client = setup_google_vision_credentials()
        print("🔐 Setting up credentials...")
        vision_client = setup_google_vision_credentials()
        nlp_client = setup_google_nlp_client()

        print("Extracting text from image...")
        text = extract_text_from_image(image_path, client)
        print("📸 Extracting text from image...")
        text = extract_text_from_image(image_path, vision_client)

        print("\nExtracting structured info...")
        info = extract_info(text)
        print("\n📊 Extracting structured info...")
        info = extract_info(text, nlp_client)

        print("\n=== OCR Output ===")
        print("\n=== 📝 OCR Output ===")
        print(text)

        print("\n=== Extracted Info ===")
        print("\n=== 🧾 Extracted Info ===")
        for key, value in info.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
