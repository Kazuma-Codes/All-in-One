import os
import fitz


class PDFMerger:
    def validate(self, input_paths, options):
        if not input_paths or len(input_paths) < 2:
            return False

        for path in input_paths:
            if not os.path.exists(path):
                return False

        return True

    def execute(self, input_paths, output_path, options):
        merged = fitz.open()

        try:
            for path in input_paths:
                doc = fitz.open(path)
                merged.insert_pdf(doc)
                doc.close()

            merged.save(output_path, garbage=4, deflate=True)
            return True

        except Exception as e:
            print(f"PDF merge failed: {e}")
            return False

        finally:
            merged.close()

    def get_metadata(self):
        return {
            "category": "pdf",
            "operation": "merge",
            "multi_input": True
        }