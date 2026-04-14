def detect(event):
	return(
		event.get("access_outside_hours", False) and
		event.get("sensitive_data_access", True)
	)
