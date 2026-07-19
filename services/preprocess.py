"""
preprocess.py

Image preprocessing for OCR using OpenCV.

Author: Monisha
Project: SmartDoc AI
"""

import os
import cv2
import numpy as np


class ImagePreprocessor:

    def __init__(self, output_folder="processed"):
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def preprocess(self, image_path):

        image_path = os.path.abspath(image_path)

        print(f"Reading: {image_path}")

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Image does not exist: {image_path}"
            )

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(
                f"OpenCV cannot read image: {image_path}"
            )

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Upscale image (improves OCR accuracy)
        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        gray = clahe.apply(gray)

        # Remove noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Otsu Threshold
        _, processed = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Small morphological cleanup
        kernel = np.ones((2, 2), np.uint8)

        processed = cv2.morphologyEx(
            processed,
            cv2.MORPH_CLOSE,
            kernel
        )

        filename = os.path.basename(image_path)

        output_path = os.path.join(
            self.output_folder,
            f"processed_{filename}"
        )

        cv2.imwrite(output_path, processed)

        print(f"Processed image saved: {output_path}")

        return output_path


if __name__ == "__main__":

    preprocessor = ImagePreprocessor()

    output = preprocessor.preprocess(
        "processed/sample_invoice_page_1.jpg"
    )

    print(output)