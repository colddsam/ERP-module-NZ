from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv()

GENAI_PROMPT = """
You are an expert receipt parser.

Return ONLY valid JSON.
Do NOT include explanations, markdown, or code blocks.
If data is missing, return null.
Normalize dates.
Fix OCR spelling errors.


JSON schema:
{
  "merchant_name": string,
  "receipt_date": "YYYY-MM-DD",
  "currency": string,
  "tax_amount": number,
  "total_amount": number,
  "items": [
    {
      "item_name": string,
      "quantity": number,
      "unit_price": number,
      "total_price": number
    }
  ]
}

OCR TEXT:
"""
GENAI_CLIENT=genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
GENAI_MODEL=os.getenv("LLM_MODEL")
GENAI_RESPONSE_SCHEMA={
                        "type": "object",
                        "properties": {
                            "merchant_name": {"type": "string"},
                            "receipt_date": {"type": "string"},
                            "currency": {"type": "string"},
                            "tax_amount": {"type": "number"},
                            "total_amount": {"type": "number"},
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item_name": {"type": "string"},
                                        "quantity": {"type": "number"},
                                        "unit_price": {"type": "number"},
                                        "total_price": {"type": "number"}
                                    },
                                    "required": [
                                        "item_name",
                                        "quantity",
                                        "unit_price",
                                        "total_price"
                                    ]
                                }
                            }
                        },
                        "required": [
                            "merchant_name",
                            "receipt_date",
                            "currency",
                            "tax_amount",
                            "total_amount",
                            "items"
                        ]
                    }