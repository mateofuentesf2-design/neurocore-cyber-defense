def evaluate_threat(event, alerts):
    severity = "low"
    action = None

    raw = event.get("raw", "").lower()

    # 🚨 REGLAS
    if "failed login" in raw and len(alerts) > 2:
        severity = "high"
        action = "block_ip"

    elif "sql" in raw:
        severity = "critical"
        action = "block_ip"

    elif "error" in raw:
        severity = "medium"

    # ML anomaly = sospechoso
    if "ml_anomaly" in alerts:
        severity = "high"
        action = "block_ip"

    return {
        "severity": severity,
        "action": action
    }