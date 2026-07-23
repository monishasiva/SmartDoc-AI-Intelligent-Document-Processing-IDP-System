"""
document_processor.py

Main document processing pipeline.

Author : Monisha
Project : SmartDoc AI
"""

import os

from services.pdf_converter import PDFConverter
from services.preprocess import ImagePreprocessor
from services.ocr import OCRService
from services.gemini_parser import GeminiParser


class DocumentProcessor:

    def __init__(self):

        self.converter = PDFConverter()

        self.preprocessor = ImagePreprocessor()

        self.ocr = OCRService()

        self.gemini = GeminiParser()

    def process_document(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":

            images = self.converter.convert_pdf(file_path)

        elif extension in [".jpg", ".jpeg", ".png"]:

            images = [file_path]

        else:

            raise ValueError("Unsupported file format")

        full_text = ""

        processed_images = []

        for image in images:

            processed = self.preprocessor.preprocess(image)

            processed_images.append(processed)

            _, text = self.ocr.extract_text(processed)

            full_text += text + "\n"

        # ------------------------
        # Gemini AI
        # ------------------------
        print("=" * 50)
        print("OCR TEXT SENT TO GEMINI")
        print("=" * 50)
        print(full_text)
        print("=" * 50)
        invoice_json = self.gemini.extract_invoice_data(
            full_text
        )

        return {

            "ocr_text": full_text,

            "invoice_data": invoice_json,

            "processed_images": processed_images

        }