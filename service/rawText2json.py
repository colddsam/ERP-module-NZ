from google.genai import types
from config.genai import GENAI_PROMPT,GENAI_CLIENT,GENAI_MODEL,GENAI_RESPONSE_SCHEMA


class RawText2JsonService:
    def __init__(self):
        self.client = GENAI_CLIENT
        self.model = GENAI_MODEL
        self.prompt = GENAI_PROMPT

    def parse_receipt(self, ocr_text: str) -> dict:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self.prompt + ocr_text,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GENAI_RESPONSE_SCHEMA
                )
            )

            return response.parsed

        except Exception as e:
            print(f"Error parsing receipt: {e}")
            return {}
