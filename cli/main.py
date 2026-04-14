import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import Engine
from core.ingestion.log_reader import follow
from core.ingestion.auth_parser import parse_auth_line
from core.ingestion.nginx_parser import parse_nginx_line
from core.ingestion.system_parser import parse_system_line

engine = Engine()

def run_auth_monitor():
	for line in follow("/var/log/auth.log"):
		event = parse_auth_line(line)
		engine.process_event(event)

def run_nginx_monitor():
	for line in follow("/var/log/nginx/access.log"):
		event = parse_system_line(line)
		engine.process_event(event)

def main():
	print("NeuroCore Defense - Real Monitoring")
	
	print("1. Monitor Auth Logs")
	print("2. Monitor Nginx Logs")
	print("3. Monitor System Logs")
	
	choice = input("Select: ")
	
	if choice == "1":
		run_auth_monitor()
	
	if choice == "2":
		run_nginx_monitor()
	
	if choice == "3":
		run_system_monitor()

if __name__ == "__main__":
	main()
