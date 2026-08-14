import requests
from fastapi import HTTPException
from ..core.config import settings


def scan_file_url(url: str) -> bool:
    """
    Replace this with a real malware scanner.

    Options:
    - ClamAV sidecar
    - VirusTotal API
    - AWS Lambda scanner
    """

    if not getattr(settings, "MALWARE_SCAN_ENDPOINT", None):
        return True

    try:
        response = requests.post(
            settings.MALWARE_SCAN_ENDPOINT,
            json={"url": url},
            timeout=30
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Malware scan failed")

        data = response.json()

        if data.get("infected"):
            return False

        return True

    except Exception:
        raise HTTPException(status_code=500, detail="Malware scan failed")