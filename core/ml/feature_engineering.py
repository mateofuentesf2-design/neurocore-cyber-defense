import re

def extract_features(event):
    raw = event.get("raw", "").lower()

    ip_match = re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", raw)

    return [
        len(raw),
        raw.count("error"),
        raw.count("failed"),
        raw.count("get"),
        raw.count("post"),
        1 if ip_match else 0,
        raw.count("login")
    ]