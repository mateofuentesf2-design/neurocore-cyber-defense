import importlib
import os

BASE_PATH = "modules"

def load_modules():
	modules = []
	
	for root, dirs, files in os.walk(BASE_PATH):
		if "detector.py" in files and "response.py" in files:
			
			module_path = root.replace("/", ".")
			
			try:
				detector = importlib.import_module(f"{module_path}.detector")
				response = importlib.import_module(f"{module_path}.response")
				
				modules.append({
					"name": module_path,
					"detector": detector,
					"response": response
				})
				
			except Exception as e:
				print(f"[ERROR] loading module {module_path}: {e}")
			
	return modules
