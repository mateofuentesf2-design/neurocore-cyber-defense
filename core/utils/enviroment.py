import platform

def get_environment():
    system = platform.system()

    if system == "Darwin":
        return "mac"
    elif system == "Linux":
        return "linux"
    elif system == "Windows":
        return "windows"
    else:
        return "unknown"