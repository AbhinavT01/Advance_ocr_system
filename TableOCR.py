import cv2
import numpy as np
import csv
import os
import tempfile
from google.cloud import vision

# ------------------ Google Credential Setup ------------------

def setup_google_vision_client():
    try:
        service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not service_account_json:
            raise EnvironmentError("❌ GOOGLE_SERVICE_ACCOUNT_JSON not set!")

        # Write service account content to a temporary JSON file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(service_account_json.encode())
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file.name

        return vision.ImageAnnotatorClient()
    except Exception as e:
        raise RuntimeError(f"🔐 Google Vision API client setup failed: {e}")

# ------------------ OCR + Table to CSV Logic ------------------

def extract_text_and_generate_csv(image_path):
    try:
        client = setup_google_vision_client()

        # Load the image
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

        # Horizontal and vertical line detection
        scale = 20
        horizontal = binary.copy()
        vertical = binary.copy()

        horizontalsize = horizontal.shape[1] // scale
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
        horizontal = cv2.erode(horizontal, horizontalStructure)
        horizontal = cv2.dilate(horizontal, horizontalStructure)

        verticalsize = vertical.shape[0] // scale
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
        vertical = cv2.erode(vertical, verticalStructure)
        vertical = cv2.dilate(vertical, verticalStructure)

        # Combine masks and find contours
        mask = cv2.add(horizontal, vertical)
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cell_data = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 20:
                cell = image[y:y + h, x:x + w]
                _, encoded_image = cv2.imencode('.jpg', cell)
                content = encoded_image.tobytes()
                vision_image = vision.Image(content=content)
                response = client.text_detection(image=vision_image)
                texts = response.text_annotations
                text = texts[0].description.strip() if texts else ""
                cell_data.append((x, y, text))

        # Sort and write CSV
        cell_data.sort(key=lambda item: (item[1], item[0]))
        image_folder = os.path.dirname(image_path)
        output_dir = os.path.join(image_folder, 'outputcsv')
        os.makedirs(output_dir, exist_ok=True)

        csv_filename = os.path.splitext(os.path.basename(image_path))[0] + '_output.csv'
        output_csv_path = os.path.join(output_dir, csv_filename)

        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            current_row = []
            previous_y = cell_data[0][1] if cell_data else 0

            for x, y, text in cell_data:
                if abs(y - previous_y) > 10:
                    writer.writerow(current_row)
                    current_row = []
                    previous_y = y
                current_row.append(text)
            if current_row:
                writer.writerow(current_row)

        print(f"✅ CSV saved at: {output_csv_path}")
        return output_csv_path

    except Exception as e:
        print(f"❌ Failed to process image and generate CSV: {e}")
        return None
