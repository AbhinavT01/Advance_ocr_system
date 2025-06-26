import re
import os
import cv2
from google.cloud import vision
from regextest import regex_detect
from human_detection import extract_person_names
from human_detection2 import extract_person_names1
from Address import parse_address
from patternfile import patterns
from cropimage import crop_image

# ✅ Write the credentials JSON content to a temp file and set the env variable
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_CONTENT"):
    with open("gcloud_key.json", "w") as f:
        f.write(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_CONTENT"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcloud_key.json"
else:
    raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS_CONTENT is not set.")

client = vision.ImageAnnotatorClient()

def main_file(image_path):
    image = cv2.imread(image_path)
    image = crop_image(image)

    _, buffer = cv2.imencode('.jpg', image)
    content = buffer.tobytes()
    vision_image = vision.Image(content=content)

    response = client.text_detection(image=vision_image)
    texts = response.text_annotations

    detected_text = texts[0].description.strip() if texts else ""
    descriptions = detected_text.split('\n')

    detected_value = " ".join(descriptions)
    print('DETECTED VALUE:', detected_value, '\n')

    # Begin Cleaning Text
    cleaned_text = detected_value.strip()
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

    print('CLEANED TEXT:', cleaned_text, '\n')
    print("LINES:", descriptions, '\n')

    persons = extract_person_names(cleaned_text)
    address = parse_address(cleaned_text)
    license_data = regex_detect(cleaned_text)

    license_data['Name'] = persons
    license_data['Street Address'] = address.get('street_full', '')
    license_data['City'] = address.get('city', '')
    license_data['State and ZIP'] = f"{address.get('state', '')} {address.get('zip_code', '')}".strip()
    license_data['All Text'] = detected_value

    print('FINAL DATA:\n', license_data, '\n')
    return license_data

# Example usage
# image_path = './sample data/idcad8.jpg'
# data = main_file(image_path)
