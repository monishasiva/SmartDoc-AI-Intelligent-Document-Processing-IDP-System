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


class DocumentProcessor:

    def __init__(self):

        self.converter = PDFConverter()

        self.preprocessor = ImagePreprocessor()

        self.ocr = OCRService()

    def process_document(self, file_path):
        """
        Complete document processing pipeline.

        Parameters
        ----------
        file_path : str

        Returns
        -------
        dict
        """

        extension = os.path.splitext(file_path)[1].lower()

        # PDF
        if extension == ".pdf":

            images = self.converter.convert_pdf(file_path)

        # Image
        elif extension in [".jpg", ".jpeg", ".png"]:

            images = [file_path]

        else:

            raise ValueError("Unsupported File Type")

        full_text = ""

        processed_images = []

        for image in images:

            processed = self.preprocessor.preprocess(image)

            processed_images.append(processed)

            _, text = self.ocr.extract_text(processed)

            full_text += text
            full_text += "\n\n"

        return {

            "text": full_text,

            "processed_images": processed_images

        }