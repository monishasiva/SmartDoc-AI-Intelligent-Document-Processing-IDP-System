"""
ocr.py

Extract text from invoices using EasyOCR.

Author : Monisha
Project : SmartDoc AI
"""

import easyocr
import os


class OCRService:

    def __init__(self):

        print("Loading EasyOCR Model...")

        self.reader = easyocr.Reader(
            ['en'],
            gpu=False
        )

        print("OCR Model Loaded Successfully.")

    def extract_text(self, image_path):

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"{image_path} not found.")

        results = self.reader.readtext(
            image_path,
            detail=0,
            paragraph=True
        )

        full_text = "\n".join(results)

        return results, full_text


if __name__ == "__main__":

    image = "processed/processed_sample_invoice_page_1.jpg"

    ocr = OCRService()

    results, text = ocr.extract_text(image)

    print("\n=========================")
    print("Extracted Invoice Text")
    print("=========================\n")

    print(text)