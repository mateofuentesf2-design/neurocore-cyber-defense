import os

def block_ip(ip):
	print(f"[ACTION] Blocking IP {ip}")
	os.system(f"sudo iptable-A INPUT -s {ip} -j DROP")
