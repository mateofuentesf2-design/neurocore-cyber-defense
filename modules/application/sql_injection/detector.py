def detect(event):
	payload = event.get("payload", "").upper()
	return "SELECT" in payload and "--" in payload
