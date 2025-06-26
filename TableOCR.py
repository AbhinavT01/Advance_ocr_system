import cv2
import numpy as np
import os
import csv
import tempfile
from google.cloud import vision

# Constants
ROW_TOLERANCE = 15  # pixels

# ------------------ Google Credential Setup ------------------

def setup_google_vision_client():
    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise EnvironmentError("❌ GOOGLE_SERVICE_ACCOUNT_JSON not set!")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(service_account_json.encode())
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file.name

    return vision.ImageAnnotatorClient()

# ------------------ Main Function: Row-Aligned Text to CSV ------------------

def extract_text_by_row_alignment(image_path):
    try:
        # Setup Vision Client
        client = setup_google_vision_client()

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Image not found: {image_path}")
            return None

        # Encode image for API
        _, encoded_image = cv2.imencode('.jpg', image)
        vision_image = vision.Image(content=encoded_image.tobytes())
        response = client.document_text_detection(image=vision_image)

        if not response.text_annotations:
            print("⚠️ No text found in image.")
            return None

        # Extract word-level bounding boxes
        boxes = []
        for annotation in response.text_annotations[1:]:  # skip full-text
            text = annotation.description.replace('\n', ' ').strip()
            vertices = annotation.bounding_poly.vertices
            if len(vertices) < 4:
                continue
            x = int(np.mean([v.x for v in vertices if v.x is not None]))
            y = int(np.mean([v.y for v in vertices if v.y is not None]))
            boxes.append((x, y, text))

        # Sort boxes top-to-bottom, then left-to-right
        boxes.sort(key=lambda b: (b[1], b[0]))

        # Group by horizontal alignment
        rows = []
        current_row = []
        prev_y = None

        for x, y, text in boxes:
            if prev_y is None or abs(y - prev_y) <= ROW_TOLERANCE:
                current_row.append((x, text))
            else:
                current_row.sort()
                rows.append([txt for _, txt in current_row])
                current_row = [(x, text)]
            prev_y = y

        if current_row:
            current_row.sort()
            rows.append([txt for _, txt in current_row])

        # Save to CSV
        output_dir = os.path.join(os.path.dirname(image_path), "outputcsv")
        os.makedirs(output_dir, exist_ok=True)
        output_csv = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0] + "_aligned.csv")

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

        print(f"✅ CSV generated successfully: {output_csv}")
        return output_csv

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None

# ------------------ Run Script ------------------

if __name__ == "__main__":
    test_image_path = "./sample_data/5.png"  # Replace with your test image
    extract_text_by_row_alignment(test_image_path)
