import os
import re
import atexit
import json
from google.cloud import vision
from google.cloud import language_v1

# ✅ Step 1: Read JSON credentials content from environment variable
creds_json_content = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_CONTENT")
creds_file_path = "google_creds.json"

if creds_json_content:
    # ✅ Step 2: Write to a temporary file
    with open(creds_file_path, "w") as f:
        f.write(creds_json_content)
    
    # ✅ Step 3: Point GOOGLE_APPLICATION_CREDENTIALS to the file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_file_path

    # ✅ Step 4 (optional): Auto-delete temp creds file on exit
    atexit.register(lambda: os.remove(creds_file_path) if os.path.exists(creds_file_path) else None)
else:
    raise EnvironmentError("Missing GOOGLE_APPLICATION_CREDENTIALS_CONTENT environment variable.")

# ✅ Step 5: Initialize Google Cloud clients
vision_client = vision.ImageAnnotatorClient()
nlp_client = language_v1.LanguageServiceClient()


# ✅ Function to extract ORGANIZATION (e.g., Bank) names from text using NLP
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
