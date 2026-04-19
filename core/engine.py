from core.normalizer import normalize_event
from core.detection.rules import rule_engine
from core.correlation.engine import correlate
from core.ml.anomaly_model import predict_anomaly, add_training_sample
from core.response.rules_engine import respond_to_alerts
from core.utils.ip_utils import is_internal_ip

def process_event(event):
    """
    Main event processing pipeline:
    1. Normalize event
    2. Apply rule-based detection
    3. Apply correlation analysis
    4. Apply ML anomaly detection
    5. Trigger automated responses
    6. Store for continuous learning
    """
    print(f"\n[EVENT RECEIVED] Source: {event.get('source', 'unknown')}")

    # 1. Normalize event
    event = normalize_event(event)

    # 2. Rule-based detection
    alerts = rule_engine(event)

    # 3. Correlation analysis
    alerts.extend(correlate(event))

    # 4. ML Anomaly Detection
    features = extract_ml_features(event)
    if predict_anomaly(features):
        alerts.append("ml_anomaly")
        # Add as positive training sample for ML
        add_training_sample(features, 1, event.get("source", "unknown"))
    else:
        # Add as negative training sample (normal)
        add_training_sample(features, 0, event.get("source", "unknown"))

    # 5. Respond to alerts (auto-block, notify, etc.)
    if alerts:
        respond_to_alerts(event, alerts)

    # 6. Store event in database for persistence and analysis
    store_event(event, alerts)

    return alerts

def extract_ml_features(event):
    """Extract features for ML model from normalized event"""
    raw = event.get("raw", "").lower()
    
    # Feature set matching the ML model expectation (8 features)
    length = len(raw)
    error_count = raw.count("error") + raw.count("fail") + raw.count("denied") + raw.count("invalid")
    failed_count = raw.count("failed") + raw.count("denied") + raw.count("invalid") + raw.count("wrong")
    get_count = raw.count("get")
    post_count = raw.count("post")
    special_chars = sum(raw.count(c) for c in ['<', '>', '\"', "'", ';', '(', ')', '&', '|', '{', '}', '[', ']'])
    numbers = sum(raw.count(str(i)) for i in range(10))
    spaces = raw.count(' ')
    
    return [
        float(length),
        float(error_count),
        float(failed_count),
        float(get_count),
        float(post_count),
        float(special_chars),
        float(numbers),
        float(spaces)
    ]

def store_event(event, alerts):
    """Store event in database with alert information"""
    try:
        from core.db import execute_insert
        
        alert_str = ",".join(alerts) if alerts else None
        severity = "high" if any(x in alerts for x in ["brute_force", "sql_injection", "ddos"]) else \
                  "medium" if any(x in alerts for x in ["port_scan", "xss"]) else \
                  "low" if alerts else "info"
        
        execute_insert("""
            INSERT INTO events (source, raw, tenant_id, ip, alert, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.get("source", "unknown"),
            event.get("raw", ""),
            event.get("tenant_id", "default"),
            event.get("ip"),
            alert_str,
            severity
        ))
    except Exception as e:
        print(f"⚠️ Error storing event: {e}")