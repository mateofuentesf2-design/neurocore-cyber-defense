import subprocess
import time
import os
import webbrowser

from core.utils.env_detector import detect_environment

env = detect_environment()
print(f"🌍 Running on: {env}")


print("🚀 Starting NeuroCore System...")

# =========================
# 1. ACTIVAR API (FastAPI)
# =========================
print("📡 Starting API server...")
api_process = subprocess.Popen(
    ["uvicorn", "backend.main:app", "--reload"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(2)

# =========================
# 2. DASHBOARD (HTTP SERVER)
# =========================
print("🌐 Starting Dashboard...")
dashboard_process = subprocess.Popen(
    ["python3", "-m", "http.server", "5500"],
    cwd="dashboard",
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(2)

# =========================
# 3. ABRIR NAVEGADOR
# =========================
print("🖥 Opening Dashboard...")
webbrowser.open("http://localhost:5500")

# =========================
# 4. EJECUTAR MONITOR
# =========================
print("🧠 Starting CLI Monitoring...\n")

subprocess.run(["python3", "-m", "cli.main"])