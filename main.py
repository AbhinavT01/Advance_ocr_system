# from flask import Flask
# app = Flask(__name__)
import re
import os
import tempfile
import cv2
from google.cloud import vision

from regextest import regex_detect
from human_detection import extract_person_names
from human_detection2 import extract_person_names1
from Address import parse_address
from patternfile import patterns
from cropimage import crop_image

# ✅ Secure Google Credential Setup
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set!")


def main_file(image_path):
    image = cv2.imread(image_path)

    image = crop_image(image)

    _, buffer = cv2.imencode('.jpg', image)
    content = buffer.tobytes()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    detected_text = texts[0].description.strip() if texts else ""
    descriptions = detected_text.split('\n')

    words = []
    detected_value = ''
    for text in texts:
        if text.description not in words:
            words.append(text.description)

    for each in descriptions:
        detected_value += " " + each

    print('detecetvelaue', detected_value, '\n')

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

    print('CLEANEDTEXT', cleaned_text, '\n')
    print("descriptions", descriptions, '\n')

    persons = extract_person_names(cleaned_text)
    print(persons)
    address = parse_address(cleaned_text)
    license_data = regex_detect(cleaned_text)

    n = len(descriptions)

    print(address)

    license_data['Name'] = persons
    license_data['Street Address'] = address['street_full']
    license_data['City'] = address['city']
    license_data['State and ZIP'] = address['state'] + " " + address['zip_code']
    license_data['All Text'] = detected_value

    print(license_data, '\n')
    return license_data


# Example usage:
# imgpath = './sample data/idcad8.jpg'
# result = main_file(imgpath)
