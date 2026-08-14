import os
from PIL import Image
from ..base import BaseConverter

class ImageConverter(BaseConverter):
    def validate(self, input_path: str, options: dict) -> bool:
        if not os.path.exists(input_path): return False
        try:
            with Image.open(input_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def execute(self, input_path: str, output_path: str, options: dict) -> bool:
        try:
            target_format = options.get("target_format", "PNG").upper()
            with Image.open(input_path) as img:
                # Handle RGBA to RGB conversion for JPEG
                if target_format == "JPEG" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Handle resizing if requested
                if "width" in options and "height" in options:
                    img = img.resize((options["width"], options["height"]))
                    
                img.save(output_path, format=target_format, quality=options.get("quality", 85))
            return True
        except Exception as e:
            print(f"Image conversion error: {e}")
            return False

    def get_metadata(self) -> dict:
        return {
            "category": "image",
            "operations": ["jpg_to_png", "png_to_jpg", "resize", "webp_to_png"],
            "options": ["target_format", "width", "height", "quality"]
        }