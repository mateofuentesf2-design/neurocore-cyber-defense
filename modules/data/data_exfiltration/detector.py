def detect(event):
	return event.get("data_transfer_md", 0) > 500
