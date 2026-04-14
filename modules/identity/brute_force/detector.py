import time
from collections import defaultdict

FAILED_LOGINS = defaultdict(int)

THRESHOLD = 5

def detect(ip):
	FAILED_LOGINS[ip] += 1
	
	if FAILED_LOGINS[ip] > THESHOLD:
		return True
	
	return False

THRESHOLD = 5

def detect(event):
	return event.get("failed_logins", 0) > THRESHOLD
