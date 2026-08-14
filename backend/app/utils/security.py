import os


def scan_local_file(path: str) -> bool:
    """
    Hook for ClamAV or another local scanner.

    Example:
      clamdscan file
    """

    if os.getenv("ENABLE_MALWARE_SCAN", "false").lower() != "true":
        return True

    # Replace with real scanner integration
    return True