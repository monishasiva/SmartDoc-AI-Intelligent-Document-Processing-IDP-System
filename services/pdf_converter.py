"""
pdf_converter.py

Converts uploaded PDF invoices into image files.

Author : Monisha
Project : SmartDoc AI
"""

import os
from pdf2image import convert_from_path
from PIL import Image


class PDFConverter:
    """
    Handles PDF to Image Conversion
    """

    def __init__(self, output_folder="processed"):
        self.output_folder = output_folder

        os.makedirs(self.output_folder, exist_ok=True)

    def convert_pdf(self, pdf_path):
        """
        Convert every page of PDF into JPEG images.

        Parameters
        ----------
        pdf_path : str

        Returns
        -------
        list
            List of generated image paths
        """

        image_paths = []

        try:
            pages = convert_from_path(
            pdf_path,
            poppler_path=r"C:\poppler-26.02.0\Library\bin"
            )
            
            filename = os.path.splitext(
                os.path.basename(pdf_path)
            )[0]

            for index, page in enumerate(pages):

                image_name = f"{filename}_page_{index+1}.jpg"

                image_path = os.path.join(
                    self.output_folder,
                    image_name
                )

                page.save(image_path, "JPEG")

                image_paths.append(image_path)

            return image_paths

        except Exception as e:

            print("PDF Conversion Error:", e)

            return []


if __name__ == "__main__":

    converter = PDFConverter()

    images = converter.convert_pdf(
        "uploads/sample_invoice.pdf"
    )

    print(images)