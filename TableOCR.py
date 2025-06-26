import tempfileAdd commentMore actions
from google.cloud import vision

# Load GCP credentials securely from environment variable
# ✅ Load GCP credentials securely from environment variable
service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if service_account_info:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
@@ -17,88 +17,132 @@

def extract_text_and_generate_csv(image_path):
    """
    Extracts tabular text from an image and writes it to a CSV using Google Cloud Vision API.
    Extracts tabular text from an image with precise cell detection.
    Uses advanced preprocessing and accurate cell sorting.
    Returns the path of the generated CSV file.
    """
    # Initialize the Vision client
    # Initialize Vision client
    client = vision.ImageAnnotatorClient()

    # Step 1: Read image and pre-process
    # Step 1: Enhanced image preprocessing
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
        if w > 50 and h > 20:
            cell = image[y:y + h, x:x + w]
            _, encoded_image = cv2.imencode('.jpg', cell)
            content = encoded_image.tobytes()
        
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
            text = texts[0].description.strip() if texts else ""
            cell_data.append((x, y, text))

    # Step 4: Sort cells row-wise then column-wise
    cell_data.sort(key=lambda item: (item[1], item[0]))

    # Step 5: Create output path
    image_folder = os.path.dirname(image_path)
    output_folder = os.path.join(image_folder, 'outputcsv')
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

    # Step 6: Write to CSV
    
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        current_row = []
        previous_y = cell_data[0][1] if cell_data else 0
        row_height = 0

        for x, y, text in cell_data:
            if abs(y - previous_y) > row_height + 10:  # adjust based on row gap
        prev_y = cell_data[0]['y'] if cell_data else 0
        
        for cell in cell_data:
            # New row detection based on row height threshold
            if abs(cell['y'] - prev_y) > avg_row_height * 0.6:
                writer.writerow(current_row)
                current_row = []
                previous_y = y
            current_row.append(text)
            row_height = max(row_height, abs(y - previous_y))  # Update row height

                prev_y = cell['y']
            
            current_row.append(cell['text'])
        
        if current_row:
            writer.writerow(current_row)

    print(f"CSV written to: {output_csv_path}")
    
    print(f"✅ Successfully generated CSV at: {output_csv_path}")
    return output_csv_path

# Example usage
# if __name__ == "__main__":
#     img_path = "./tablesample.png"
#     csv_result = extract_text_and_generate_csv(img_path)
# Example usage:
if __name__ == "__main__":
    img_path = input("Enter image path: ").strip()
    if os.path.exists(img_path):
        csv_result = extract_text_and_generate_csv(img_path)
        print(f"Results saved to: {csv_result}")
    else:
        print("Error: Image file not found")
