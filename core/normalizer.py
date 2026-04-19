def normalize_event(event):
    raw = event.get("raw", "").lower()

    normalized = {
        "source": event.get("source", "unknown"),
        "raw": raw,
        "timestamp": event.get("timestamp"),
        "ip": extract_ip(raw),
        "method": "get" if "get" in raw else "post" if "post" in raw else None,
        "status": extract_status(raw),
        "user": extract_user(raw),
    }

    return normalized


def extract_ip(raw):
    import re
    match = re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", raw)
    return match.group(0) if match else None


def extract_status(raw):
    if "error" in raw:
        return "error"
    if "failed" in raw:
        return "failed"
    return "ok"


def extract_user(raw):
    if "user" in raw:
        return "user_detected"
    return None