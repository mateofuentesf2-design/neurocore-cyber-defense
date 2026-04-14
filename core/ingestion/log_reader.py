import time

def follow(file_path):
	with open(file_path, "r") as file:
		file.seek(0, 2)
		
		while True:
			line = file.readline()
			if not line:
				time.sleep(0.2)
				continue
			yield line
