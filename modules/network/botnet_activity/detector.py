def detect(event):
	return event.get("connections_to_blacklist", 0) > 3
