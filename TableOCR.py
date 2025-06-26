import os
import cv2
import csv
import numpy as np
import tempfile
from google.cloud import vision

# Load GCP credentials securely from environment variable
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON not set!")

def extract_text_and_generate_csv(image_path):
    """
    Extracts tabular text from an image and writes it to a CSV using Google Cloud Vision API.
    Returns the path of the generated CSV file.
    """
    # Initialize the Vision client
    client = vision.ImageAnnotatorClient()

    # Step 1: Read image and pre-process
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                   cv2.THRESH_BINARY, 15, -2)

    # Step 2: Extract table structure
    horizontal = binary.copy()
    vertical = binary.copy()
    scale = 20  # Adjust based on table size

    # Horizontal lines
    h_size = horizontal.shape[1] // scale
    h_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1))
    horizontal = cv2.erode(horizontal, h_structure)
    horizontal = cv2.dilate(horizontal, h_structure)

    # Vertical lines
    v_size = vertical.shape[0] // scale
    v_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size))
    vertical = cv2.erode(vertical, v_structure)
    vertical = cv2.dilate(vertical, v_structure)

    # Step 3: Combine lines to get cell boxes
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

    # Step 4: Sort cells row-wise then column-wise
    cell_data.sort(key=lambda item: (item[1], item[0]))

    # Step 5: Create output path
    image_folder = os.path.dirname(image_path)
    output_folder = os.path.join(image_folder, 'outputcsv')
    os.makedirs(output_folder, exist_ok=True)

    csv_filename = os.path.splitext(os.path.basename(image_path))[0] + '_output.csv'
    output_csv_path = os.path.join(output_folder, csv_filename)

    # Step 6: Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        current_row = []
        previous_y = cell_data[0][1] if cell_data else 0
        row_height = 0

        for x, y, text in cell_data:
            if abs(y - previous_y) > row_height + 10:  # adjust based on row gap
                writer.writerow(current_row)
                current_row = []
                previous_y = y
            current_row.append(text)
            row_height = max(row_height, abs(y - previous_y))  # Update row height

        if current_row:
            writer.writerow(current_row)

    print(f"CSV written to: {output_csv_path}")
    return output_csv_path

# Example usage
# if __name__ == "__main__":
#     img_path = "./tablesample.png"
#     csv_result = extract_text_and_generate_csv(img_path)
