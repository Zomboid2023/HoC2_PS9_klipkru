import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        if not os.path.exists(image_path):
            return None

        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip() if text else None
    except Exception as e:
        print(f"[ERROR] OCR extraction failed: {e}")
        return None
