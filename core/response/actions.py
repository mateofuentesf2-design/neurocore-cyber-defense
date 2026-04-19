import os

def block_ip(ip):
    if not ip:
        return

    print(f"[BLOCKING IP] {ip}")

    try:
        os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
    except:
        print("⚠️ Could not block IP")


def respond(event, alerts):

    ip = event.get("ip")

    for alert in alerts:

        print(f"[🚨 ALERT] {alert}")

        # 🔥 acciones críticas
        if alert in ["brute_force_attack", "ddos_attack"]:
            block_ip(ip)