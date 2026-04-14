def extract_features(event):
	return [
		event.get("packet_size", 0)
		event.get("request_rate", 0)
		event.get("faild_logins", 0)
		event.get("duration", 0)
	]
	
