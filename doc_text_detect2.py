import os
from google.cloud import vision

# ✅ Correctly load credentials from environment variable and write to file
creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_CONTENT")
if creds_json:
    with open("google_creds.json", "w") as f:
        f.write(creds_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"
else:
    raise EnvironmentError("Missing GOOGLE_APPLICATION_CREDENTIALS_CONTENT environment variable.")

def detect_document_text(image_path):
    """Detects document text in an image."""
    # Initialize the client
    client = vision.ImageAnnotatorClient()

    # Read the image file
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    # Construct the image
    image = vision.Image(content=content)

    # Perform document text detection
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f'API Error: {response.error.message}')

    annotations = response.full_text_annotation

    if annotations:
        formatted_text = annotations.text
        print('Detected document text:')
        print(formatted_text)
        return formatted_text
    else:
        return 'No document text detected.'

# if __name__ == "__main__":
#     image_path = './images1.jpg'
#     detect_document_text(image_path)
