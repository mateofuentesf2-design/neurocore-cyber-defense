def parse_system_line(line):
	event ={}
	
	if "sudo" in line:
		event["privilege_change"]=True
	
	if "session opened" in line:
		event["login_event"] = True
	
	return event if event else None
