import request
from core.config import load_config

config = load_config()

def send_event(event):
	request.post(
		config["api"]["endpoint"],
		json=event,
		headers={"Autorization": f"Bearer {config['api']['api_key]}"}
	)
	
