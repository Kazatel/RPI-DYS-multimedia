import subprocess
import time
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config



def bluetoothctl_command(commands):
    """Send a sequence of commands to bluetoothctl."""
    try:
        subprocess.run(
            ["bluetoothctl"],
            input="\n".join(commands) + "\n",
            text=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_device_status(mac):
    """Check if device is paired, trusted, and connected."""
    try:
        output = subprocess.check_output(
            ["bluetoothctl", "info", mac], text=True
        )
        paired = "Paired: yes" in output
        trusted = "Trusted: yes" in output
        connected = "Connected: yes" in output
        return paired, trusted, connected
    except subprocess.CalledProcessError:
        return False, False, False


def pair_gamepad(name):
    mac = config.GAMEPADS.get(name)
    if not mac:
        print(f"❌ Gamepad '{name}' not found in config.")
        return False

    print(f"\n🎮 Preparing to pair '{name}' ({mac})")

    while True:
        input("➡️  Put the gamepad in pairing mode, then press ENTER to continue...")

        print("🔗 Attempting to pair, trust, and connect...")
        bluetoothctl_command([
            "power on",
            f"pair {mac}",
            f"trust {mac}",
            f"connect {mac}",
            "exit"
        ])

        print("⏳ Verifying status, please wait...")
        time.sleep(3)

        paired, trusted, connected = check_device_status(mac)

        if all([paired, trusted, connected]):
            print(f"✅ '{name}' paired, trusted, and connected successfully!")
            return True
        else:
            print("❌ Device not fully connected. Status:")
            print(f"   Paired:   {paired}")
            print(f"   Trusted:  {trusted}")
            print(f"   Connected:{connected}")
            print("🔁 Let's try again...\n")


def connect_gamepad(name):
    mac = config.GAMEPADS.get(name)
    if not mac:
        print(f"❌ Gamepad '{name}' not found in config.")
        return False

    print(f"🔗 Connecting to gamepad '{name}' ({mac})...")
    if bluetoothctl_command(["power on", f"connect {mac}", "exit"]):
        print(f"✅ Successfully connected to {name}.")
        return True
    else:
        print(f"❌ Failed to connect to {name}.")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python bluetooth_manager.py pair <gamepad_name>")
        print("  python bluetooth_manager.py connect <gamepad_name>")
    else:
        action = sys.argv[1].lower()
        gamepad_name = sys.argv[2]
        if action == "pair":
            pair_gamepad(gamepad_name)
        elif action == "connect":
            connect_gamepad(gamepad_name)
        else:
            print(f"Unknown action '{action}'. Use 'pair' or 'connect'.")
