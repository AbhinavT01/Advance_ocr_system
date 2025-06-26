import os
import re
from google.cloud import vision
from google.cloud import language_v1

# ✅ FIX: Write JSON from environment to file and point the SDK to it
creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_CONTENT")
if creds_json:
    with open("google_creds.json", "w") as f:
        f.write(creds_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"
else:
    raise EnvironmentError("Missing GOOGLE_APPLICATION_CREDENTIALS_CONTENT environment variable.")

# Initialize clients after setting credentials
vision_client = vision.ImageAnnotatorClient()
nlp_client = language_v1.LanguageServiceClient()

def analyze_entities(text):
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

# Example:
# text = "Payment made using American Express issued by Chase Bank."
# print(analyze_entities(text))
