import os
import json
import tempfile
from google.cloud import language_v1

# Step 1: Load service account JSON from environment variable (used in Render)
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

# Step 2: Write to a temporary file for Google Cloud SDK to use
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set!")

# ------------------ PERSON NAME EXTRACTOR ------------------
def extract_person_names(text):
    """
    Extracts the most relevant person name from text using Google Cloud NLP API.
    Filters out generic terms like 'driver' or 'safe'.
    Prioritizes names based on salience and truncates long names to 3 words max.
    """
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT
    )

    response = client.analyze_entities(document=document)

    person_name = "any_name"  # default fallback
    top_salience = 0.0

    for entity in response.entities:
        if language_v1.Entity.Type(entity.type_) == language_v1.Entity.Type.PERSON:
            if entity.salience > top_salience and entity.name.lower() not in ['driver', 'safe']:
                words = entity.name.split()
                if len(words) > 3:
                    person_name = ' '.join(words[:3])
                else:
                    person_name = entity.name
                top_salience = entity.salience

    return person_name
