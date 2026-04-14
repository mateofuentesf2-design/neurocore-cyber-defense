from core.module_loader import load_modules
from core.ml.anomaly_model import AnomalyDetector
from core.response.actions import block_ip

class Engine:
	
	def __init__(self):
		self.modules = load_modules()
		self.ml = AnomalyDetector()
		self.state = {}
		
	def process_event(self, event):
		if not event:
			return
		
		ip = event.get("ip")
		
		# Acumuladores reales
		if ip:
			self.state.setdefult(ip, {
				"failed_logins": 0,
				"request_rate": 0
			})
			
			if "failed_login" in event:
				self.state[ip]["failed_logins"] += 1
			
			if "request_rate" in event:
				self.state[ip]["request_rate"] += 1
			
			event.update(self.state[ip])
		
		#ML
		features =[
			event.get("failed_logins", 0),
			event.get("request_rate", 0),
			event.get("data_transfer_mb", 0),
			event.get("duration", 0)
		]
		
		if self.ml.predict(features):
			print("[ML] anomaly detected")
		
		#Modulos
		for module in self.modules:
			try:
				if module["detector"].detect(event):
					print(f"[ALERT] {module['name']}")
					
					if ip:
						block_ip(ip)
					module["response"].respond(event)
					
			except Exception as e:
				print(f"Error in module {module['name']}: {e}")
			
