def detect(event):
    raw = event.get("raw", "").lower()

    return "sudo" in raw or "privilege" in raw or "root access" in raw