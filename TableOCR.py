import cv2
import numpy as np
import os
import csv
import tempfile
from google.cloud import vision

ROW_TOLERANCE = 15  # pixel tolerance for row alignment

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

def extract_text_and_generate_csv(image_path):
    try:
        client = setup_google_vision_client()

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Encode image for API
        _, encoded_image = cv2.imencode('.jpg', image)
        vision_image = vision.Image(content=encoded_image.tobytes())

        # Perform text detection
        response = client.document_text_detection(image=vision_image)
        if not response.text_annotations:
            print("⚠️ No text found in image.")
            return None

        # Get word-level annotations
        boxes = []
        for annotation in response.text_annotations[1:]:  # Skip full text
            text = annotation.description.replace('\n', ' ').strip()
            vertices = annotation.bounding_poly.vertices
            if len(vertices) < 4:
                continue
            x = int(np.mean([v.x for v in vertices if v.x is not None]))
            y = int(np.mean([v.y for v in vertices if v.y is not None]))
            boxes.append((x, y, text))

        # Sort and group into rows
        boxes.sort(key=lambda b: (b[1], b[0]))
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

        # Create output folder and file path
        output_dir = os.path.join(os.path.dirname(image_path), "outputcsv")
        os.makedirs(output_dir, exist_ok=True)
        output_csv_path = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(image_path))[0] + "_aligned.csv"
        )

        # Write to CSV
        with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

        print(f"✅ CSV saved to: {output_csv_path}")
        return output_csv_path

    except Exception as e:
        print(f"❌ Failed to process table: {e}")
        return None
