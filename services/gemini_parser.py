"""
gemini_parser.py

SmartDoc AI
Google Gen AI SDK
"""

import json

from google import genai

from config import Config


class GeminiParser:

    def __init__(self):

        self.client = genai.Client(
            api_key=Config.GEMINI_API_KEY
        )

    def extract_invoice_data(self, ocr_text):

        prompt = f"""
You are an Intelligent Document Processing System.

Extract the invoice information.

Return ONLY valid JSON.

Schema:

{{
  "vendor_name": null,
  "invoice_number": null,
  "invoice_date": null,
  "gst_number": null,
  "subtotal": null,
  "tax_amount": null,
  "total_amount": null
}}

OCR TEXT:

{ocr_text}
"""
        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        print("=" * 50)
        print("GEMINI RESPONSE")
        print("=" * 50)
        print(response.text)
        print("=" * 50)
       
        try:
            return json.loads(response.text)

        except json.JSONDecodeError:

            return {
                "error": "Gemini did not return valid JSON",
                "raw_response": response.text
            }