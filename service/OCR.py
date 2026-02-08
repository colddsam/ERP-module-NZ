import io
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import cv2
import numpy as np


class OCRService:

    def _processing(self, image: Image.Image) -> np.ndarray:
        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 3)
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return thresh

    def extract_text_from_image(self, image: Image.Image) -> str:
        processed = self._processing(image)
        return pytesseract.image_to_string(
            Image.fromarray(processed),
            config="--psm 6"
        )

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        pages = convert_from_bytes(pdf_bytes)
        text = ""
        for page in pages:
            text += self.extract_text_from_image(page)
        return text

    def extract_text(self, file_bytes: bytes, content_type: str) -> str:
        if content_type.startswith("image/"):
            image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            return self.extract_text_from_image(image)

        if content_type == "application/pdf":
            return self.extract_text_from_pdf_bytes(file_bytes)

        raise ValueError("Unsupported file type")
