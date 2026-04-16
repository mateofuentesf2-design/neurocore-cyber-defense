import subprocess
import platform

def block_ip(ip):
    system = platform.system()

    try:
        if system == "Linux":
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])

        elif system == "Darwin":
            subprocess.run(["sudo", "pfctl", "-t", "blocklist", "-T", "add", ip])

        elif system == "Windows":
            subprocess.run([
                "netsh", "advfirewall", "firewall",
                "add", "rule",
                f"name=Block_{ip}",
                "dir=in", "action=block",
                f"remoteip={ip}"
            ])

        print(f"[🔥 FIREWALL] IP BLOCKED: {ip}")

    except Exception as e:
        print(f"[FIREWALL ERROR] {e}")