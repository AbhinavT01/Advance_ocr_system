import os
import re
import cv2
import tempfile
from google.cloud import vision

from regextest import regex_detect
from human_detection import extract_person_names
from human_detection2 import extract_person_names1
from Address import parse_address
from patternfile import patterns
from cropimage import crop_image

# Securely set Google credentials from environment variable
def setup_google_credentials():
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

# Main processing logic using text detection
def main_file(image_path):
    try:
        # Load and crop image
        image = cv2.imread(image_path)
        image = crop_image(image)

        # Encode image to bytes
        _, buffer = cv2.imencode('.jpg', image)
        content = buffer.tobytes()

        # Google Vision API Client
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=content)

        # Perform OCR
        response = client.text_detection(image=image)
        if response.error.message:
            raise Exception(f"Vision API Error: {response.error.message}")
        
        texts = response.text_annotations
        detected_text = texts[0].description.strip() if texts else ""
        descriptions = detected_text.split('\n')

        # Collect all words
        words = []
        for text in texts:
            if text.description not in words:
                words.append(text.description)

        detected_value = " ".join(descriptions)
        print('Detected Text:', detected_value, '\n')

        # Clean the extracted text
        cleaned_text = detected_value.strip().replace('\n', ' ')
        cleaned_text = re.sub(r'(?<=\s)\d{2}\s\d{2}(?=\s)', '', cleaned_text)
        cleaned_text = re.sub(r'(?<!\S)\d(?!\S)|(?<!\S)\d{1}(?!\S)', '', cleaned_text)
        cleaned_text = re.sub(r'(?<=\s)[a-z]\d\s(?=\s)|(?<=\s)\d[a-z]\s(?=\s)', '', cleaned_text)
        cleaned_text = re.sub(r'(?<=\s)\d{2}\s(?=\s)|(?<=\s)\s\d{2}(?=\s)', '', cleaned_text)
        cleaned_text = re.sub(r'\b(?:4a|4b)\b', '', cleaned_text)
        cleaned_text = re.sub(r'(?<=[a-zA-Z])1(?=[a-zA-Z])', 'I', cleaned_text)
        cleaned_text = re.sub(r'[^\w\s/:,\-\'".#]', '', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        cleaned_text = re.sub(r'\bDD\d{10,}\b', '', cleaned_text)
        cleaned_text = re.sub(r'(?<=\s)(?:4[a-z]|[a-z]4)(?=\s)', '', cleaned_text, flags=re.IGNORECASE)

        print('Cleaned Text:', cleaned_text, '\n')
        print("Descriptions:", descriptions, '\n')

        # Named entity & regex based extraction
        persons = extract_person_names(cleaned_text)
        address = parse_address(cleaned_text)
        license_data = regex_detect(cleaned_text)

        license_data['Name'] = persons
        license_data['Street Address'] = address['street_full']
        license_data['City'] = address['city']
        license_data['State and ZIP'] = f"{address['state']} {address['zip_code']}"
        license_data['All Text'] = detected_value

        print("\n--- Extracted Data ---\n")
        print(license_data)
        return license_data

    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

# Optional: Document-style OCR (alternative usage)
def detect_document_text(image_path):
    try:
        client = vision.ImageAnnotatorClient()
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")

        annotations = response.full_text_annotation
        if annotations and annotations.text:
            print("Detected Document Text:\n")
            print(annotations.text.strip())
            return annotations.text.strip()
        else:
            return "No document text detected."

    except Exception as e:
        return f"Error during OCR: {str(e)}"

# Entry point
if __name__ == "__main__":
    setup_google_credentials()
    image_path = "./images1.jpg"  # Change to your test image
    result = main_file(image_path)
    print("\n--- Final Output ---\n")
    print(result)
