import os
import json
import tempfile
from google.cloud import vision

# Step 1: Load service account JSON from environment variable
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

# Step 2: Write it to a temporary file so Google client libraries can use it
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set!")

# Step 3: Define OCR function
def detect_document_text(image_path):
    """
    Detects text from a document-style image using Google Vision API.

    Args:
        image_path (str): Local path to the image file.

    Returns:
        str: Extracted text or error message.
    """
    try:
        # Initialize the Vision API client
        client = vision.ImageAnnotatorClient()

        # Read the image content
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Call document_text_detection
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")

        annotations = response.full_text_annotation

        if annotations and annotations.text:
            formatted_text = annotations.text.strip()
            print("Detected document text:\n")
            print(formatted_text)
            return formatted_text
        else:
            return "No document text detected."

    except Exception as e:
        return f"Error occurred during OCR: {str(e)}"

# Optional CLI interface for testing
if __name__ == "__main__":
    image_path = "./images1.jpg"  # Change to your actual test image path
    result = detect_document_text(image_path)
    print("\n--- Result ---\n")
    print(result)
