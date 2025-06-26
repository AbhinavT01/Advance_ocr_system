import os
import re
import cv2
import json
import tempfile
from google.cloud import vision
from regextest import regex_detect
from human_detection import extract_person_names
from human_detection2 import extract_person_names1
from Address import parse_address
from patternfile import patterns
from cropimage import crop_image

# 1️⃣ Read credentials securely from env variable
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

# 2️⃣ Main processing function
def main_file(image_path):
    image = cv2.imread(image_path)

    # Optional: rotate image if needed
    # image = auto_rotate(image)

    image = crop_image(image)  # Crop borders or noise
    _, buffer = cv2.imencode('.jpg', image)
    content = buffer.tobytes()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    # 3️⃣ OCR using Google Vision
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        raise ValueError("No text detected in the image.")

    detected_text = texts[0].description.strip()
    descriptions = detected_text.split('\n')

    detected_value = " ".join(descriptions)
    print("Raw Detected Text:", detected_value, "\n")

    # 4️⃣ Clean OCR'd text
    cleaned_text = detected_value
    cleaned_text = cleaned_text.replace('\n', ' ')
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

    print("Cleaned Text:", cleaned_text, "\n")
    print("Line-wise OCR:", descriptions, "\n")

    # 5️⃣ Entity Extraction
    persons = extract_person_names(cleaned_text)
    address = parse_address(cleaned_text)
    license_data = regex_detect(cleaned_text)

    # 6️⃣ Assemble structured results
    license_data['Name'] = persons
    license_data['Street Address'] = address['street_full']
    license_data['City'] = address['city']
    license_data['State and ZIP'] = f"{address['state']} {address['zip_code']}".strip()
    license_data['All Text'] = detected_value

    print("Final Extracted License Data:\n", license_data, '\n')
    return license_data

# 🧪 Example usage
# if __name__ == "__main__":
#     img_path = './sample data/idcad8.jpg'
#     result = main_file(img_path)
