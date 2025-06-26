import os
import re
import csv
import cv2
import numpy as np
from google.cloud import vision

# ✅ Fix: Convert service account JSON content from env var to a temporary file
creds_content = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_CONTENT')
if creds_content:
    with open("gcloud_key.json", "w") as f:
        f.write(creds_content)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcloud_key.json"
else:
    raise EnvironmentError("Missing GOOGLE_APPLICATION_CREDENTIALS_CONTENT environment variable.")

# Initialize the Google Cloud Vision client
client = vision.ImageAnnotatorClient()

def extract_text_and_generate_csv(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to get binary image
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

    # Structure detection
    horizontal = binary.copy()
    vertical = binary.copy()
    scale = 20

    horizontalsize = horizontal.shape[1] // scale
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    verticalsize = vertical.shape[0] // scale
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    # Combine horizontal and vertical lines
    mask = cv2.add(horizontal, vertical)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))

    # Find contours (cells)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cell_data = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 20:  # filter noise
            cell = image[y:y+h, x:x+w]
            _, encoded_image = cv2.imencode('.jpg', cell)
            content = encoded_image.tobytes()

            vision_image = vision.Image(content=content)
            response = client.text_detection(image=vision_image)
            texts = response.text_annotations
            text = texts[0].description if texts else ""
            cell_data.append((x, y, text.strip()))

    cell_data.sort(key=lambda item: (item[1], item[0]))

    image_folder = os.path.dirname(image_path)
    csv_filename = os.path.splitext(os.path.basename(image_path))[0] + '_output.csv'
    output_dir = os.path.join(image_folder, 'outputcsv')
    os.makedirs(output_dir, exist_ok=True)
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

    print(f"CSV file saved at: {output_csv_path}")
    return output_csv_path
