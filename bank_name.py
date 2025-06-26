import os
import re
from google.cloud import vision
from google.cloud import language_v1
from google.oauth2 import service_account

# ✅ Step 1: Directly embed the JSON credentials
credentials_info = {
  "type": "service_account",
  "project_id": "aerobic-botany-464022-t6",
  "private_key_id": "6ac5f02a7707e8251b35ffc296fe5c80c97bb406",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8V5kX0oF5bpad\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "advanceocr@aerobic-botany-464022-t6.iam.gserviceaccount.com",
  "client_id": "112282222414363959436",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/advanceocr%40aerobic-botany-464022-t6.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# ✅ Step 2: Create credentials object
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# ✅ Step 3: Initialize clients with embedded credentials
vision_client = vision.ImageAnnotatorClient(credentials=credentials)
nlp_client = language_v1.LanguageServiceClient(credentials=credentials)

# ✅ Function to extract ORGANIZATION (e.g., Bank) names using NLP
def analyze_entities(text):
    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    response = nlp_client.analyze_entities(document=document, encoding_type='UTF8')

    bank_names = []
    for entity in response.entities:
        if language_v1.Entity.Type(entity.type_).name == "ORGANIZATION":
            bank_names.append(entity.name)

    return sorted(set(bank_names))

# # ✅ Example Usage
# if __name__ == "__main__":
#     sample_text = """
#         Payment was made using American Express issued by Chase Bank.
#         Another account is with Wells Fargo and Capital One.
#     """
#     banks = analyze_entities(sample_text)
#     print("Detected Bank/Organization Names:", banks)
