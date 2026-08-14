CONVERSION_REGISTRY = {
    "image.jpg_to_png": {
        "category": "image",
        "source_format": "jpg",
        "target_format": "png"
    },
    "image.png_to_jpg": {
        "category": "image",
        "source_format": "png",
        "target_format": "jpg"
    },
    "image.ocr_to_text": {
        "category": "image",
        "source_format": "image",
        "target_format": "txt"
    },
    "pdf.compress": {
        "category": "pdf",
        "source_format": "pdf",
        "target_format": "pdf"
    },
    "pdf.merge": {
        "category": "pdf",
        "source_format": "pdf",
        "target_format": "pdf"
    },
    "pdf.split": {
        "category": "pdf",
        "source_format": "pdf",
        "target_format": "zip"
    },
    "pdf.ocr": {
        "category": "pdf",
        "source_format": "pdf",
        "target_format": "pdf"
    },
    "document.docx_to_pdf": {
        "category": "document",
        "source_format": "docx",
        "target_format": "pdf"
    },
    "audio.to_mp3": {
        "category": "audio",
        "source_format": "audio",
        "target_format": "mp3"
    },
    "audio.to_wav": {
        "category": "audio",
        "source_format": "audio",
        "target_format": "wav"
    }
}


def get_supported_conversions():
    return {
        "image": [
            "image.jpg_to_png",
            "image.png_to_jpg",
            "image.ocr_to_text"
        ],
        "pdf": [
            "pdf.compress",
            "pdf.merge",
            "pdf.split",
            "pdf.ocr"
        ],
        "document": [
            "document.docx_to_pdf"
        ],
        "audio": [
            "audio.to_mp3",
            "audio.to_wav"
        ]
    }