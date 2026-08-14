import os
import ocrmypdf


class PDFOCRConverter:
    def validate(self, input_path, options):
        return os.path.exists(input_path)

    def execute(self, input_path, output_path, options):
        try:
            ocrmypdf.ocr(
                input_path,
                output_path,
                language=options.get("language", "eng"),
                skip_text_on_error=True,
                progress_bar=False
            )

            return True

        except Exception as e:
            print(f"PDF OCR failed: {e}")
            return False

    def get_metadata(self):
        return {
            "category": "pdf",
            "operation": "ocr"
        }