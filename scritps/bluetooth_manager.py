import subprocess
import time
import os
import sys

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
        output = subprocess.check_output(
            ["bluetoothctl", "info", mac], text=True
        )
        paired = "Paired: yes" in output
        trusted = "Trusted: yes" in output
        connected = "Connected: yes" in output
        return paired, trusted, connected
    except subprocess.CalledProcessError:
        return False, False, False


def pair_gamepad(name, mac):
    print(f"\n🎮 Preparing to pair '{name}' ({mac})")

    while True:
        input("➡️  Put the gamepad in pairing mode, then press ENTER to continue...")

        print("🔍 Scanning for devices...")
        bluetoothctl_command([
            "power on",
            "agent on",
            "default-agent",
            "scan on"
        ])
        time.sleep(5)

        print("🔗 Attempting to pair, trust, and connect...")
        bluetoothctl_command([
            f"pair {mac}",
            f"trust {mac}",
            f"connect {mac}",
            "scan off",
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
            print(f"   Paired:    {paired}")
            print(f"   Trusted:   {trusted}")
            print(f"   Connected: {connected}")
            print("🔁 Let's try again...\n")


def main():
    for name, mac in config.GAMEPADS.items():
        success = pair_gamepad(name, mac)
        if not success:
            print(f"❌ Failed to pair {name} after multiple attempts.")
        else:
            print(f"✅ Finished pairing {name}.\n")


if __name__ == "__main__":
    main()
