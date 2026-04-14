def detect(event):
	payload = event.get("payload", "").lower()
	return "<script>" in payload
