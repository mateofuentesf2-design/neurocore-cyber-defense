def detect(event):
	return event.get("anomally_score", 0) > 0.9
