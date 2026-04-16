import re

def extract_ip(text):
    match = re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", text)
    return match.group(0) if match else None