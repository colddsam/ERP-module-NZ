import pytesseract
from dotenv import load_dotenv
import os

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
