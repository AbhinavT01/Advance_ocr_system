import os
import re
import tempfile
from google.cloud import vision
from google.cloud import language_v1

def setup_google_credentials():
    """
    Sets up Google credentials from the environment variable 'GOOGLE_SERVICE_ACCOUNT_JSON'.
    """
    try:
        service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if service_account_info:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
                temp.write(service_account_info.encode())
                temp_path = temp.name
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
        else:
            raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set!")
    except Exception as e:
        raise RuntimeError(f"Credential setup failed: {str(e)}")

def initialize_clients():
    """
    Initializes Google Vision and NLP clients.
    """
    try:
        vision_client = vision.ImageAnnotatorClient()
        nlp_client = language_v1.LanguageServiceClient()
        return vision_client, nlp_client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Cloud clients: {str(e)}")

def analyze_entities(text, nlp_client):
    """
    Uses Google Cloud NLP API to detect organization entities (e.g., bank names) in the text.

    Args:
        text (str): Input text to analyze.
        nlp_client: An instance of LanguageServiceClient.

    Returns:
        List[str]: Detected organization names.
    """
    try:
        document = language_v1.Document(
            content=text,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )

        response = nlp_client.analyze_entities(
            document=document,
            encoding_type='UTF8'
        )

        bank_names = []
        for entity in response.entities:
            if language_v1.Entity.Type(entity.type_).name == "ORGANIZATION":
                bank_names.append(entity.name)

        return bank_names

    except Exception as e:
        print(f"Error during NLP entity analysis: {str(e)}")
        return []

# Optional: OCR using Vision API to extract text from image
def extract_text_from_image(image_path, vision_client):
    """
    Extracts raw text from an image using Google Vision API.

    Args:
        image_path (str): Path to the image.
        vision_client: An instance of ImageAnnotatorClient.

    Returns:
        str: Extracted text.
    """
    try:
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = vision_client.text_detection(image=image)

        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")

        texts = response.text_annotations
        return texts[0].description if texts else ""

    except Exception as e:
        print(f"Error during Vision OCR: {str(e)}")
        return ""

# Entry point
if __name__ == "__main__":
    try:
        setup_google_credentials()
        vision_client, nlp_client = initialize_clients()

        image_path = "./images1.jpg"  # Update with your image path
        extracted_text = extract_text_from_image(image_path, vision_client)
        print("Extracted Text:\n", extracted_text)

        bank_names = analyze_entities(extracted_text, nlp_client)
        print("\nDetected Bank/Organization Names:\n", bank_names)

    except Exception as err:
        print(f"Fatal Error: {err}")
