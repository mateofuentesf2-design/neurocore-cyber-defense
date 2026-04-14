def detect(event):
	return event.get("missing_csrf_token", False)
