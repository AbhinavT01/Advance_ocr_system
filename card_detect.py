import os
import re
import cv2
from PIL import Image
from google.cloud import vision
import pytesseract as tes
from skimage import io, img_as_float
import imquality.brisque as brisque
from human_detection import extract_person_names
from bank_name import analyze_entities
from google.oauth2 import service_account

# ✅ Embed the service account credentials
credentials_info = {
  "type": "service_account",
  "project_id": "aerobic-botany-464022-t6",
  "private_key_id": "6ac5f02a7707e8251b35ffc296fe5c80c97bb406",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8V5kX0oF5bpad\nzgEWCO4KtU0oWbWlXYYnMySml5CCaeZgFSEXefKaOH2cgC8zgLc+VVaeheReTSdS\nuIMkhDV/cWJEAOkLUtNr6cD2QdMFYnY3KOTg2Tbmoc8EEsoX/QqOSPY6sWpZgnC1\nbpCZ3s8aPUhFWq7fGkYNt882vBRL3t1U091pNDV3il8R9/ZVu80d6S/WnYlYng48\nn8HX4kHqM80Tiae61HwyUeXNbLML+AOoyLI+HCefFkuMDM8EBhXVzmvKwyJFJlwP\n+L49FpeeL0JTnkseDrkCB1IhmUhu1JDQHLYyf+lMd17EWlY1oOu2NDLS889PmREX\n1LQcoOJrAgMBAAECggEAPQUge6BfBGm48J2aqnnwLZX5zpXqDQ6U9URTnonCbw5C\nbmTKGOIQoLimsbqyEDymodJiQu/cQlU65UkUbBNNheHFVYT5/Ao0p2TPeLlw1fDF\nni9ooBSf/e70tDwmL8lyzxCCfheW/jMNsyqEPOX8MWMjdBziRTQs+CrSPsiGxuF5\nQ/tX18Y222/jUsFKpOFzH8EIeTc59Bszl8Y6hnt8Kvcy3eBxJiU3veqAvTNkl26R\n7id2+sDAnI1+TUYuIGuo4rbFv7byfYWRYe1wHHltPfhD+qwaSzSisUB3D+6eWOQd\n7ALZY+pbtX0OFeuchuZ1JxW4+VQrJrU/hEsnRtp08QKBgQD69fhjh/Ipd2the5vi\nQgPrX7QjJca7wI0amat8cNoS9mE4FAnUWUw5wmVhFukYmM8/emgpRp/tArUHSVAb\nAA+Bfho9Bp/zB0H9NUh0AVZTMGcGAGjo3sK7wd5EBzmrjsFlHlAQ7rZqk/VKuqNB\n6aVCLcZJ2HUi71pAJ8V8fLmCgwKBgQDAH77FbQGuOkYLjaW3SVuA1z9CRIyj6PPp\nJcJv5+TWXcvtwjMGMWKrBwoobzu2McYXA5hbH+Diz21AtO6yj7oisQxS26nqbbI6\nVBoQHwNwSU31CNRpgG2Rg2YR/hehgs+I6lkdBuEw4m6ftxUIIzIGeLV6W4ywg00s\nSOvcMtR7+QKBgCbswdMGQfxGhoQ/POVyIdN/K5yL/nAepIQss5mAk4J/boLZMNEb\n7KPE0B6oBA2JnhOVc9R7HNERK2zu5Rra/oyyN3Whsmtqg8S3X/6GOpJ6nnAi3iLI\ncmHW5xecG0jNwpdhhT+rFuYe/tvRaQMPL0+9c9T+WuTJRTFQOeReIBPrAoGBALxR\noZ5FJiOQbT4/3tLU7gNReWlMZgr4ebTr1TX5uP5CvHTWKUuFtvBrmxJdTctd6IyA\ncqPHkJjht3Z4o4yVg18j6i+Br4Dhe5TfARkSPT2gLPDlccfkIgJDKRaz2Jfw79qF\n00m3h55yJPsa61upnAxp34ELIdGXMlsZM1AI5uyJAoGAWkJh+iKmBVlOEM+mcYn4\nDFmiG1nvexdbOUYpRvj6ft7ObilBZ7ZIm8dYzWckSdsrj2zbomTMtBuS8IIrRTaQ\nC/i6e9RTz5xAPVsHXrD4AWFKWx14EMqkcmswTEG6DJsRhBVdGhvkhzeBNLLZhrMn\nu7bo0JVeiTy2T9vwej46WoY=\n-----END PRIVATE KEY-----\n",
  "client_email": "advanceocr@aerobic-botany-464022-t6.iam.gserviceaccount.com",
  "client_id": "112282222414363959436",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/advanceocr%40aerobic-botany-464022-t6.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Regex patterns
card_number_pattern = r'\b(?:\d[ -]*?){13,16}\b'
expiry_date_pattern = r'\b\d{2}/\d{2}\b'
card_type_pattern = r'(?i)\b(?:VISA|Master\s*Card|MasterCard|Debit|Credit|American\s*Express|Discover|JCB|Diners\s*Club|Union\s*Pay)\b'

# OCR from image using Google Vision
def extract_text_from_image(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if response.error.message:
        raise Exception(f'{response.error.message}')
    return texts[0].description if texts else ""

# Extract key fields using regex + NLP
def extract_info(text):
    info = {
        'Card Number': re.findall(card_number_pattern, text),
        'Expiry Date': re.findall(expiry_date_pattern, text),
        'Bank Name': analyze_entities(text),
        'Card Type': re.findall(card_type_pattern, text),
        'Card Holder Name': extract_person_names(text)
    }
    return info

# Uncomment for local test
# image_path = './Bank-Cards-Reader/card2.png'
# text = extract_text_from_image(image_path)
# print(extract_info(text))
