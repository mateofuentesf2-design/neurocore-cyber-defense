from core.response.firewall import block_ip
from core.response.rules_engine import evaluate_threat
from core.response.audit import log_action
from core.utils.ip_utils import extract_ip

def process_event(event):
    print("\n==============================")
    print("[EVENT RECEIVED]")
    print(event)

    # 🔥 enviar a API
    send_event_to_api(event)

    alerts = []

    # 🔍 DETECCIÓN POR MÓDULOS
    for module_name, module in modules.items():
        try:
            if module["detector"](event):
                alerts.append(module_name)
        except Exception as e:
            print(f"[MODULE ERROR - {module_name}] {e}")

    # 🧠 MACHINE LEARNING
    try:
        features = extract_features(event)
        if detect_anomaly(features):
            alerts.append("ml_anomaly")
    except Exception as e:
        print(f"[ML ERROR] {e}")

    # 🚨 RESULTADOS
    if alerts:
        print(f"\n[🚨 ALERTS DETECTED: {len(alerts)}]")
        for alert in alerts:
            print(f" - {alert}")

        # 🧠 DECISIÓN INTELIGENTE
        decision = evaluate_threat(event, alerts)

        severity = decision["severity"]
        action = decision["action"]

        print(f"[SEVERITY] {severity}")

        # 🌐 EXTRAER IP
        ip = extract_ip(event.get("raw", ""))

        # 🔥 EJECUTAR RESPUESTA
        if action == "block_ip" and ip:
            block_ip(ip)
            log_action(event, action, severity)

    else:
        print("[OK] No threats detected")