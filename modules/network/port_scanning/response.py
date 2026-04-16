def respond(event):
    ip = event.get("ip", "unknown")
    print(f"[RESPONSE] Potential port scan from {ip}")