import re

# Simple regex patterns for common IOCs
IOC_PATTERNS = {
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "url": r"https?://[^\s<>\"]+",
    "hash": r"\b[a-fA-F0-9]{32,64}\b"
}

def extract_iocs(text):
    """
    Extract IOCs from a given string.
    Returns a dictionary of IPs, URLs, Hashes.
    """
    if not text:
        return {"ipv4": [], "url": [], "hash": []}

    return {
        "ipv4": re.findall(IOC_PATTERNS["ipv4"], text),
        "url": re.findall(IOC_PATTERNS["url"], text),
        "hash": re.findall(IOC_PATTERNS["hash"], text)
    }
