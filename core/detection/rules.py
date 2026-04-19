def rule_engine(event):
    raw = event["raw"]
    alerts = []

    # 🔐 AUTH
    if "failed login" in raw:
        alerts.append("brute_force")

    if "password incorrect" in raw:
        alerts.append("credential_attack")

    # 🌐 WEB
    if "select" in raw or "union" in raw:
        alerts.append("sql_injection")

    if "<script>" in raw:
        alerts.append("xss")

    if "file upload" in raw:
        alerts.append("malicious_upload")

    # 🌐 NETWORK
    if "port scan" in raw:
        alerts.append("port_scanning")

    if "ddos" in raw:
        alerts.append("ddos_attack")

    # 🖥 ENDPOINT
    if "chmod 777" in raw:
        alerts.append("privilege_escalation")

    if "wget http" in raw or "curl http" in raw:
        alerts.append("malware_download")

    # 📦 DATA
    if "large transfer" in raw:
        alerts.append("data_exfiltration")

    return alerts