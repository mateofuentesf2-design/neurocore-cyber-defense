import re

LOG_REGEX = re.compile(r'(\d+\.\d+\.\d+\.\d+).*"(GET|POST).*" (\d+)')

def parse_ngix_line(line):
	match = LOG_REGEX.search(line)
	if not match:
		return None
	
	ip = match.group(1)
	
	return {
		"type": "http_request",
		"ip": ip,
		"request_rate": 1
		"pauload": line
	}
