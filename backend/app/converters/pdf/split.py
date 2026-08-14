import os
import fitz
import zipfile
import tempfile


class PDFSplitter:
    def validate(self, input_path, options):
        return os.path.exists(input_path)

    def execute(self, input_path, output_path, options):
        try:
            doc = fitz.open(input_path)

            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for page_number in range(len(doc)):
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp_path = tmp.name

                    new_doc.save(tmp_path)
                    new_doc.close()

                    zip_file.write(tmp_path, arcname=f"page_{page_number + 1}.pdf")
                    os.remove(tmp_path)

            doc.close()
            return True

        except Exception as e:
            print(f"PDF split failed: {e}")
            return False

    def get_metadata(self):
        return {
            "category": "pdf",
            "operation": "split",
            "output": "zip"
        }