def detect(event):
	return event.get("file_encryption_rate", 0) > 100
