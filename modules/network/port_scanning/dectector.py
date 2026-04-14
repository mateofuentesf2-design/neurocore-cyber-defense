def detect(event):
	return event.get("ports_accessed", 0) > 50
