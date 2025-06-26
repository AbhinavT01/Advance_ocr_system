import os
import cv2
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
import tempfile
from collections import defaultdict

def extract_table_to_excel(image_path):
    """Extract tables from image with accurate row/column mapping to Excel"""
    
    # Initialize PaddleOCR (more accurate for tables than Google Vision)
    ocr = PaddleOCR(use_angle_cls=True, lang='en', 
                   ocr_version='PP-OCRv4', 
                   show_log=False)

    # Enhanced image processing
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Noise reduction and binarization
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, 11, 4)

    # Detect table structure
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours for cells
    contours, _ = cv2.findContours(dilate, cv2.RETR_TREE, 
                                 cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter and sort contours (LTR, Top-Bottom)
    contours = sorted([cv2.boundingRect(c) for c in contours 
                      if cv2.contourArea(c) > 500], 
                     key=lambda x: (x[1]//20, x[0]))  # Row tolerance = 20px

    # Extract text and group by rows/columns
    table_data = defaultdict(dict)
    row_tolerance = 20  # px tolerance for same row
    
    for idx, (x,y,w,h) in enumerate(contours):
        cell_img = img[y:y+h, x:x+w]
        
        # OCR with Paddle (better than Google for tables)
        result = ocr.ocr(cell_img, cls=True)
        text = result[0][0][1][0] if result else ""
        
        # Determine row (group y coordinates within tolerance)
        row_key = None
        for existing_y in sorted(table_data.keys()):
            if abs(y - existing_y) <= row_tolerance:
                row_key = existing_y
                break
        if row_key is None:
            row_key = y
            
        # Store by row then x coordinate
        table_data[row_key][x] = text

    # Convert to DataFrame
    rows = []
    for y in sorted(table_data.keys()):
        row_texts = []
        for x in sorted(table_data[y].keys()):
            row_texts.append(table_data[y][x])
        rows.append(row_texts)
    
    df = pd.DataFrame(rows).fillna("")

    # Create Excel file
    output_dir = os.path.join(os.path.dirname(image_path), "output_excel")
    os.makedirs(output_dir, exist_ok=True)
    
    excel_path = os.path.join(output_dir, 
                            f"{os.path.splitext(os.path.basename(image_path))[0]}_output.xlsx")
    
    df.to_excel(excel_path, index=False, header=False)
    print(f"Excel file saved to: {excel_path}")
    return excel_path

# Example usage
if __name__ == "__main__":
    image_path = "your_table_image.png"  # Replace with your image
    if os.path.exists(image_path):
        excel_file = extract_table_to_excel(image_path)
    else:
        print("Error: Image file not found")
