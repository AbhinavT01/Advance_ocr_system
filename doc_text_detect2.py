import os
import json
from google.cloud import vision
from google.oauth2 import service_account

def detect_document_text(image_path):
    """Detects document text in an image."""

    # Get JSON credentials from environment variable
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS_JSON is not set.")

    # Parse the string into a dictionary and restore newlines
    service_account_info = json.loads(creds_json)
    service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

    # Create credentials object
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # Initialize the client with credentials
    client = vision.ImageAnnotatorClient(credentials=credentials)

    # Read the image file
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    # Construct the image
    image = vision.Image(content=content)

    # Perform document text detection
    response = client.document_text_detection(image=image)

    # Check for API errors
    if response.error.message:
        raise Exception(f'Google Vision API Error: {response.error.message}')

    annotations = response.full_text_annotation

    if annotations and annotations.text:
        formatted_text = annotations.text
        print('Detected document text:')
        print(formatted_text)
        return formatted_text
    else:
        return 'No document text detected.'

# For local testing:
# if __name__ == "__main__":
#     image_path = './images1.jpg'
#     detect_document_text(image_path)
