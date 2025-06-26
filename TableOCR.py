import os
import cv2
import csv
import numpy as np
import tempfile
from google.cloud import vision

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
    """
    Extracts tabular text from an image with precise cell detection.
    Uses advanced preprocessing and accurate cell sorting.
    Returns the path of the generated CSV file.
    """
    # Initialize Vision client
    client = vision.ImageAnnotatorClient()

    # Step 1: Enhanced image preprocessing
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Noise removal and thresholding
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    binary = cv2.adaptiveThreshold(~blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                 cv2.THRESH_BINARY, 21, -5)

    # Step 2: Precise table structure detection
    horizontal = np.copy(binary)
    vertical = np.copy(binary)
    
    # Dynamic scaling based on image size
    scale = int(max(image.shape) * 0.02)  # 2% of image dimension
    scale = max(scale, 10)  # Minimum scale of 10
    
    # Detect horizontal lines with morphological operations
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (scale, 1))
    horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, h_kernel, iterations=2)
    
    # Detect vertical lines
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, scale))
    vertical = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, v_kernel, iterations=2)
    
    # Combine horizontal and vertical lines
    grid = cv2.addWeighted(horizontal, 0.5, vertical, 0.5, 0.0)
    grid = cv2.erode(~grid, kernel=np.ones((2,2), np.uint8), iterations=1)
    
    # Step 3: Accurate cell detection
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours that are too small
    min_area = image.shape[0] * image.shape[1] * 0.0002  # 0.02% of image area
    contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    cell_data = []
    
    # Sort contours from top to bottom, left to right
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    (contours, bounding_boxes) = zip(*sorted(
        zip(contours, bounding_boxes),
        key=lambda b: (b[1][1], b[1][0])  # Sort by y then x
    ))
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Extract cell with border padding
        border = 2
        cell = image[max(0,y-border):y+h+border, max(0,x-border):x+w+border]
        
        # Convert to bytes for Vision API
        _, encoded_image = cv2.imencode('.png', cell)
        content = encoded_image.tobytes()
        
        try:
            vision_image = vision.Image(content=content)
            response = client.text_detection(image=vision_image)
            texts = response.text_annotations
            text = texts[0].description.replace('\n', ' ').strip() if texts else ""
            cell_data.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'text': text
            })
        except Exception as e:
            print(f"Error processing cell at ({x},{y}): {str(e)}")
            cell_data.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'text': ""
            })
    
    # Step 4: Advanced table reconstruction
    # Calculate average row height and column width
    if len(cell_data) > 0:
        row_heights = np.array([c['height'] for c in cell_data])
        avg_row_height = np.median(row_heights)
        
        col_widths = np.array([c['width'] for c in cell_data])
        avg_col_width = np.median(col_widths)
    
    # Step 5: Write structured CSV
    output_folder = os.path.join(os.path.dirname(image_path), 'outputcsv')
    os.makedirs(output_folder, exist_ok=True)
    csv_filename = os.path.splitext(os.path.basename(image_path))[0] + '_output.csv'
    output_csv_path = os.path.join(output_folder, csv_filename)
    
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        current_row = []
        prev_y = cell_data[0]['y'] if cell_data else 0
        
        for cell in cell_data:
            # New row detection based on row height threshold
            if abs(cell['y'] - prev_y) > avg_row_height * 0.6:
                writer.writerow(current_row)
                current_row = []
                prev_y = cell['y']
            
            current_row.append(cell['text'])
        
        if current_row:
            writer.writerow(current_row)
    
    print(f"✅ Successfully generated CSV at: {output_csv_path}")
    return output_csv_path

# Example usage:
if __name__ == "__main__":
    img_path = input("Enter image path: ").strip()
    if os.path.exists(img_path):
        csv_result = extract_text_and_generate_csv(img_path)
        print(f"Results saved to: {csv_result}")
    else:
        print("Error: Image file not found")
