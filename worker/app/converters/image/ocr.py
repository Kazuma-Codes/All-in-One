import os
from PIL import Image
import pytesseract


class ImageOCRConverter:
    def validate(self, input_path, options):
        return os.path.exists(input_path)

    def execute(self, input_path, output_path, options):
        try:
            img = Image.open(input_path)
            text = pytesseract.image_to_string(img)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            return True

        except Exception as e:
            print(f"OCR failed: {e}")
            return False

    def get_metadata(self):
        return {
            "category": "image",
            "operation": "ocr_to_text"
        }