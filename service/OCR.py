import pytesseract
from PIL import Image
from config import OCR

class OCRService:
    def __init__(self):
        pass
    
    def extract_text_from_image(self,image: Image.Image) -> str:
        return pytesseract.image_to_string(image, config="--psm 6")