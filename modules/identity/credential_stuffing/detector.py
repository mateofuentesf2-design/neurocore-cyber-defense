def detect(event):
	return (
		event.get("login_attempts", 0) > 20 and
		event.get("unique_accounts", 0) > 10
	)
	
