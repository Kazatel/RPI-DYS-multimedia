import subprocess
import time
import os
import sys
import re

# Add parent directory to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


def bluetoothctl_command(commands, suppress_output=True):
    """Send a sequence of commands to bluetoothctl."""
    try:
        result = subprocess.run(
            ["bluetoothctl"],
            input="\n".join(commands) + "\n",
            text=True,
            check=True,
            capture_output=not suppress_output
        )
        return result.stdout if not suppress_output else True
    except subprocess.CalledProcessError as e:
        print(f"❌ bluetoothctl error: {e}")
        return False


def check_device_status(mac):
    """Check if device is paired, trusted, and connected."""
    try:
        output = subprocess.check_output(["bluetoothctl", "info", mac], text=True)
        paired = "Paired: yes" in output
        trusted = "Trusted: yes" in output
        connected = "Connected: yes" in output
        return paired, trusted, connected
    except subprocess.CalledProcessError:
        return False, False, False


def connect_gamepad(name):
    """Connect a gamepad from config."""
    mac = config.GAMEPADS.get(name)
    if not mac:
        print(f"❌ Gamepad '{name}' not found in config.")
        return False

    print(f"🔗 Connecting to gamepad '{name}' ({mac})...")
    bluetoothctl_command(["power on"])
    bluetoothctl_command([f"connect {mac}"])

    print("⏳ Verifying status, please wait...")
    time.sleep(3)
    paired, trusted, connected = check_device_status(mac)

    if connected:
        print(f"✅ Successfully connected to {name}.")
        return True
    else:
        print("❌ Failed to connect. Status:")
        print(f"   Paired:    {paired}")
        print(f"   Trusted:   {trusted}")
        print(f"   Connected: {connected}")
        return False


# ─────────────── INTERACTIVE PAIRING MODE ─────────────── #

def discover_devices(scan_time=8):
    """Scan for Bluetooth devices and return dict of MAC -> Name."""
    print("🔍 Scanning for Bluetooth devices...")
    proc = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    proc.stdin.write("scan on\n")
    proc.stdin.flush()
    time.sleep(scan_time)
    proc.stdin.write("scan off\nexit\n")
    proc.stdin.flush()

    output, _ = proc.communicate()
    devices = {}
    for line in output.splitlines():
        match = re.search(r"Device ([\w:]+) (.+)", line)
        if match:
            mac, name = match.groups()
            devices[mac] = name
    return devices


def pick_device(devices):
    """Allow user to pick a device from scanned list."""
    print("\n📡 Found devices:")
    choices = list(devices.items())
    for i, (mac, name) in enumerate(choices):
        print(f"{i + 1}. {name} ({mac})")
    choice = int(input("👉 Enter the number of the device to pair: ")) - 1
    return choices[choice]


def pair_device(mac):
    """Attempt to pair/trust/connect a device by MAC."""
    print(f"\n🔗 Pairing with {mac}...")
    output = bluetoothctl_command([
        "power on",
        "agent on",
        "default-agent",
        f"pair {mac}",
        f"trust {mac}",
        f"connect {mac}",
    ], suppress_output=False)

    return "successful" in output.lower()


def pair_mode():
    """Run interactive pairing flow."""
    devices = discover_devices()
    if not devices:
        print("❌ No devices found. Try again.")
        return

    mac, name = pick_device(devices)
    success = pair_device(mac)
    if not success:
        print("❌ Pairing failed. Try again.")
        return

    print("⏳ Verifying connection...")
    time.sleep(3)
    paired, trusted, connected = check_device_status(mac)

    print(f"\n🔎 Final Status:")
    print(f"   Paired:    {paired}")
    print(f"   Trusted:   {trusted}")
    print(f"   Connected: {connected}")

    if all([paired, trusted, connected]):
        print(f"✅ {name} connected successfully!")
    else:
        print(f"⚠️  Something went wrong, but pairing might still have partially succeeded.")


# ─────────────── ENTRY POINT ─────────────── #

def usage():
    print("Usage:")
    print("  python bluetooth_manager.py pair")
    print("  python bluetooth_manager.py connect <gamepad_name>")
    print("\nAvailable gamepads:")
    for name in config.GAMEPADS:
        print(f"  - {name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    action = sys.argv[1]

    if action == "pair":
        pair_mode()
    elif action == "connect" and len(sys.argv) == 3:
        connect_gamepad(sys.argv[2])
    else:
        usage()
