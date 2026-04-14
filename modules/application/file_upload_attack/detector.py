def detect(event):
	filename = event.get("filename", "")
	return filename.endswith(".exe") or filename.endswith(".sh")
