import os

def block_ip(ip):
	os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
