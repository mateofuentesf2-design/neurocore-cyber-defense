import os
import platform

def detect_environment():
    system = platform.system()

    if os.path.exists("/var/log"):
        return "server"

    if system == "Darwin":
        return "mac"

    return "unknown"