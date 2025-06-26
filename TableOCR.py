import osAdd commentMore actions
import cv2
import numpy as np
import csv
import numpy as np
import tempfile
from google.cloud import vision
import os

# ✅ Load GCP credentials securely from environment variable
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(service_account_info.encode())
        temp_path = temp.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
else:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON not set!")

def extract_text_and_generate_csv(image_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'myservicegapi.json'
    
    # Initialize the Google Cloud Vision client
    """
    Extracts tabular text from an image and writes it to a CSV using Google Cloud Vision API.
    Returns the path of the generated CSV file.
    """
    # Initialize the Vision client
    client = vision.ImageAnnotatorClient()

    # Load the image
    # Step 1: Read image and pre-process
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                   cv2.THRESH_BINARY, 15, -2)

    # Apply adaptive thresholding to invert the image and get a binary image
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

    # Create horizontal and vertical structures
    # Step 2: Extract table structure
    horizontal = binary.copy()
    vertical = binary.copy()
    scale = 20  # Adjust based on table size

    # Define a size for the morphology operation
    scale = 20

    # Detect horizontal lines
    horizontalsize = horizontal.shape[1] // scale
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)
    # Horizontal lines
    h_size = horizontal.shape[1] // scale
    h_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1))
    horizontal = cv2.erode(horizontal, h_structure)
    horizontal = cv2.dilate(horizontal, h_structure)

    # Detect vertical lines
    verticalsize = vertical.shape[0] // scale
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)
    # Vertical lines
    v_size = vertical.shape[0] // scale
    v_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size))
    vertical = cv2.erode(vertical, v_structure)
    vertical = cv2.dilate(vertical, v_structure)

    # Combine horizontal and vertical lines
    # Step 3: Combine lines to get cell boxes
    mask = cv2.add(horizontal, vertical)

    # Dilate the grid to ensure clear cell separation
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))

    # Find contours of the grid cells
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # List to store extracted text with their bounding box coordinates
    cell_data = []

    # Iterate through each detected contour
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Filter out small contours that might be noise
        if w > 50 and h > 20:
            # Extract the cell from the image
            cell = image[y:y + h, x:x + w]

            # Convert the cell to a byte array
            _, encoded_image = cv2.imencode('.jpg', cell)
            content = encoded_image.tobytes()

            # Create an image object for Google Cloud Vision API
            vision_image = vision.Image(content=content)

            # Perform text detection on the cell image
            response = client.text_detection(image=vision_image)
            texts = response.text_annotations
            text = texts[0].description.strip() if texts else ""
            cell_data.append((x, y, text))

            # Extract the detected text
            text = texts[0].description if texts else ""

            # Store the extracted text along with the coordinates
            cell_data.append((x, y, text.strip()))

    # Sort the cell data by y-coordinate (primary) and x-coordinate (secondary)
    # Step 4: Sort cells row-wise then column-wise
    cell_data.sort(key=lambda item: (item[1], item[0]))

    # Generate the output CSV file path
    # Step 5: Create output path
    image_folder = os.path.dirname(image_path)
    output_folder = os.path.join(image_folder, 'outputcsv')
    os.makedirs(output_folder, exist_ok=True)

    csv_filename = os.path.splitext(os.path.basename(image_path))[0] + '_output.csv'
    output_csv_path = os.path.join(image_folder, 'outputcsv', csv_filename)
    output_csv_path = os.path.join(output_folder, csv_filename)

    # Write the extracted text into a CSV file
    # Step 6: Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Initialize the row list
        current_row = []
        previous_y = cell_data[0][1]
        previous_y = cell_data[0][1] if cell_data else 0

        for x, y, text in cell_data:
            if abs(y - previous_y) > 10:  # Adjust the threshold based on the spacing between rows
            if abs(y - previous_y) > 10:  # adjust based on row gap
                writer.writerow(current_row)
                current_row = []
                previous_y = y

            current_row.append(text)

        # Write the last row
        if current_row:
            writer.writerow(current_row)
    print(output_csv_path)

    print(f"CSV written to: {output_csv_path}")
    return output_csv_path

# # Usage example
# # Example usage
# if __name__ == "__main__":
#     image_path = './image.png'
#     csv_path = extract_text_and_generate_csv(image_path)
#     print(f"CSV file saved at: {csv_path}")
#     img_path = "./tablesample.png"
#     csv_result = extract_text_and_generate_csv(img_path)
