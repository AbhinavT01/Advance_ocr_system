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

        # Load image and preprocess
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 15, -2)

        # Detect horizontal and vertical lines
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

        # Combine lines and find contours
        mask = cv2.add(horizontal, vertical)
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = [cv2.boundingRect(cnt) for cnt in contours
                 if cv2.boundingRect(cnt)[2] > 50 and cv2.boundingRect(cnt)[3] > 20]

        # Sort by Y (top to bottom), then X (left to right)
        boxes = sorted(boxes, key=lambda b: (b[1], b[0]))

        # Group boxes into rows
        rows = []
        row_threshold = 10  # pixels
        for box in boxes:
            x, y, w, h = box
            added = False
            for row in rows:
                if abs(row[0][1] - y) < row_threshold:
                    row.append(box)
                    added = True
                    break
            if not added:
                rows.append([box])

        # Sort each row left to right
        for row in rows:
            row.sort(key=lambda b: b[0])

        # Extract text from each cell using Vision API
        table_data = []
        for row in rows:
            row_data = []
            for x, y, w, h in row:
                cell_img = image[y:y+h, x:x+w]
                _, encoded_image = cv2.imencode('.jpg', cell_img)
                content = encoded_image.tobytes()
                vision_image = vision.Image(content=content)
                response = client.text_detection(image=vision_image)
                texts = response.text_annotations
                text = texts[0].description.strip().replace('\n', ' ') if texts else ""
                row_data.append(text)
            table_data.append(row_data)

        # Save output to CSV
        output_dir = os.path.join(os.path.dirname(image_path), 'outputcsv')
        os.makedirs(output_dir, exist_ok=True)
        output_csv_path = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0] + '_output.csv')

        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(table_data)

        print(f"✅ CSV saved at: {output_csv_path}")
        return output_csv_path

    except Exception as e:
        print(f"❌ Error during table extraction: {e}")
        return None

# ------------------ Example Usage ------------------

# if __name__ == "__main__":
#     path = "your_table_image.png"
#     extract_text_and_generate_csv(path)
