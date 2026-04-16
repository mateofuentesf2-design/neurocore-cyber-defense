import time
import random

# 👇 IMPORT CORRECTO DESDE ENGINE
from core.engine import process_event

import requests

def send_event_to_api(event):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/events",
            json=event,
            headers={
                "x-api-key": "abc123securekey"
            }
        )

        print("[API RESPONSE]", response.status_code)

    except Exception as e:
        print("[API ERROR]", e)

def run_system_monitor(callback=None):
    print("[INFO] Monitoring SYSTEM logs")

    while True:
        try:
            # 🔥 Simulación de eventos (puedes luego reemplazar por logs reales)
            event = {
                "source": "system",
                "raw": random.choice([
                    "ERROR failed login attempt from 192.168.1.1",
                    "User login success",
                    "GET /api/data",
                    "POST /login failed",
                    "System running normally"
                ])
            }

            print("\n==============================")
            print("[EVENT GENERATED]")
            print(event)

            # ✅ USAR ENGINE CENTRAL
            process_event(event)

            time.sleep(2)

        except Exception as e:
            print("[SYSTEM MONITOR ERROR]", e)