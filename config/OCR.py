import pytesseract
from dotenv import load_dotenv
import os

load_dotenv()

if os.getenv("TESSERACT_PATH") is not None:
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
