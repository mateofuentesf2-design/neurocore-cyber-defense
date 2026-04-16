import sys
import os
import platform

# ==============================
# CONFIGURACIÓN DE PATH
# ==============================

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ==============================
# IMPORTS CORRECTOS
# ==============================

from core.ingestion.log_reader import follow
from core.ingestion.auth_parser import parse_auth_line
from core.ingestion.nginx_parser import parse_nginx_line
from core.ingestion.system_parser import run_system_monitor
from core.engine import process_event
from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()

# ==============================
# CONEXIONES ACTIVAS
# ==============================

active_connections: List[WebSocket] = []

# ==============================
# WEBSOCKET ENDPOINT
# ==============================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

# ==============================
# BROADCAST
# ==============================

async def broadcast_event(event: dict):
    for connection in active_connections:
        try:
            await connection.send_json(event)
        except:
            pass

# ==============================
# DETECCIÓN DE SISTEMA
# ==============================

SYSTEM = platform.system()

if SYSTEM == "Darwin":
    AUTH_LOG = "/var/log/system.log"
else:
    AUTH_LOG = "/var/log/auth.log"

NGINX_LOG = "/var/log/nginx/access.log"

# ==============================
# MONITORES
# ==============================

def run_auth_monitor():
    print(f"[INFO] Monitoring AUTH logs: {AUTH_LOG}")

    for line in follow(AUTH_LOG):
        try:
            event = parse_auth_line(line)

            if event:
                process_event(event)

        except Exception as e:
            print(f"[AUTH PARSER ERROR] {e}")


def run_nginx_monitor():
    print(f"[INFO] Monitoring NGINX logs: {NGINX_LOG}")

    for line in follow(NGINX_LOG):
        try:
            event = parse_nginx_line(line)

            if event:
                process_event(event)

        except Exception as e:
            print(f"[NGINX PARSER ERROR] {e}")


def run_system_logs():
    print("[INFO] Monitoring SYSTEM logs")

    try:
        run_system_monitor(process_event)
    except Exception as e:
        print(f"[SYSTEM MONITOR ERROR] {e}")

# ==============================
# CLI PRINCIPAL
# ==============================

def main():
    print("\n==============================")
    print("🧠 NeuroCore Cyber Defense")
    print("==============================")

    print("1. Monitor Auth Logs")
    print("2. Monitor Nginx Logs")
    print("3. Monitor System Logs")
    print("4. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        run_auth_monitor()

    elif choice == "2":
        run_nginx_monitor()

    elif choice == "3":
        run_system_logs()

    elif choice == "4":
        print("Exiting...")
        sys.exit(0)

    else:
        print("[ERROR] Invalid option")

# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":
    main()