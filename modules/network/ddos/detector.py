def detect(event):
	return event.get("request_rate", 0) >100
