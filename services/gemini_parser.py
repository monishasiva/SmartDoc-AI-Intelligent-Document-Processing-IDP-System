"""
gemini_parser.py

AI Invoice Information Extractor

Project : SmartDoc AI
"""

import json
import google.generativeai as genai

from config import Config


class GeminiParser:

    def __init__(self):

        genai.configure(
            api_key=Config.GEMINI_API_KEY
        )

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

    def extract_invoice_data(self, text):

        prompt = f"""
You are an Intelligent Document Processing system.

Extract the following information from the invoice.

Return ONLY valid JSON.

Fields:

vendor_name

invoice_number

invoice_date

gst_number

subtotal

tax_amount

total_amount

OCR TEXT:

{text}
"""

        response = self.model.generate_content(prompt)

        try:

            cleaned = response.text.replace("```json", "").replace("```", "").strip()

            return json.loads(cleaned)

        except Exception:

            return {
                "raw_response": response.text
            }