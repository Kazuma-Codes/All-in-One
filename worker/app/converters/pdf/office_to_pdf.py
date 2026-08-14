import os
import subprocess
import shutil
from ..base import BaseConverter


class OfficeToPDFConverter(BaseConverter):
    def validate(self, input_path, options):
        return os.path.exists(input_path)

    def execute(self, input_path, output_path, options):
        try:
            outdir = os.path.dirname(output_path)

            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    outdir,
                    input_path
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(result.stderr)
                return False

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            generated_path = os.path.join(outdir, f"{base_name}.pdf")

            if generated_path != output_path:
                shutil.move(generated_path, output_path)

            return True

        except Exception as e:
            print(f"Office conversion failed: {e}")
            return False

    def get_metadata(self):
        return {
            "category": "document",
            "operation": "office_to_pdf"
        }