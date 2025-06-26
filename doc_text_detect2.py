import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import vision_v1
import google.auth.credentials

# ✅ 1. Read credentials from Render environment variable
service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if not service_account_json:
    raise Exception("❌ GOOGLE_SERVICE_ACCOUNT_JSON env var not set!")

# ✅ 2. Parse JSON string to dict
try:
    service_account_info = json.loads(service_account_json)
except json.JSONDecodeError as e:
    raise Exception("❌ Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON") from e

# ✅ 3. Create credentials and access token
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(Request())
access_token = credentials.token

# ✅ 4. Wrap token in custom class
class SimpleTokenCredentials(google.auth.credentials.Credentials):
    def __init__(self, token):
        super().__init__()
        self._token = token

    @property
    def expired(self): return False
    @property
    def valid(self): return True
    def refresh(self, request): pass
    @property
    def token(self): return self._token

# ✅ 5. Use Vision API
manual_token_creds = SimpleTokenCredentials(access_token)
client = vision_v1.ImageAnnotatorClient(credentials=manual_token_creds)

def detect_document_text(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision_v1.Image(content=content)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"❌ Vision API error: {response.error.message}")

    annotations = response.full_text_annotation
    if annotations and annotations.text:
        print("📄 Detected Text:\n")
        print(annotations.text)
        return annotations.text
    else:
        print("⚠️ No text detected.")
        return ""

# ✅ Example usage
if __name__ == "__main__":
    image_path = "images1.jpg"  # Replace with your image path
    detect_document_text(image_path)
