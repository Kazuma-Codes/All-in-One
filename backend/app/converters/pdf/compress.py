import fitz  # PyMuPDF
from ..base import BaseConverter


class PDFCompressor(BaseConverter):
    def validate(self, input_path: str, options: dict) -> bool:
        try:
            doc = fitz.open(input_path)
            doc.close()
            return True
        except Exception:
            return False

    def execute(self, input_path: str, output_path: str, options: dict) -> bool:
        try:
            doc = fitz.open(input_path)
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            return True
        except Exception as e:
            print(f"PDF compression error: {e}")
            return False

    def get_metadata(self) -> dict:
        return {
            "category": "pdf",
            "operations": ["compress"],
            "options": ["quality"]
        }