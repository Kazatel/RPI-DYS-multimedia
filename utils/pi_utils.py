import subprocess

def get_raspberry_pi_model():
    try:
        with open("/proc/device-tree/model", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        try:
            result = subprocess.run(["cat", "/sys/firmware/devicetree/base/model"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return "Unknown"
