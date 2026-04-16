def detect(event):
    raw = event.get("raw", "").lower()

    keywords = [
        "scan",
        "nmap",
        "port scan",
        "syn scan",
        "probing"
    ]

    return any(k in raw for k in keywords)