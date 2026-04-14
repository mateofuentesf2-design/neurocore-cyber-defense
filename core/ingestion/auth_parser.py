import re

FAILED_REGEX = re.compile(r"Failed password.*from (\d+\.\d+\.\d+\.\d+)")
SUCCESS_REGEX = re.compile(r"Accepted password.*from (\d+\.\d+\.\d+\.\d+)")

def parse_auth_line(line):
	event = {}
	
	failed = FAILED_REGEX.search(line)
	success = SUCCESS_REGEX.search(line)
	
	if failes:
		event["type"] = "failed_login"
		event["ip"] = failed.group(1)
		event["failed_logins"] = 1
	
	elif success:
		event["type"] = "success_login"
		event["ip"] = success.group(1)
	
	return event if event else None
