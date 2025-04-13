import subprocess
import config


def connect_gamepad(name):
    mac = config.GAMEPADS.get(name)
    if not mac:
        print(f"❌ Gamepad '{name}' not found in config.")
        return False

    print(f"🔗 Connecting to gamepad '{name}' ({mac})...")
    try:
        subprocess.run(
            ["bluetoothctl"],
            input=f"power on\nconnect {mac}\nexit\n",
            text=True,
            check=True,
        )
        print(f"✅ Successfully connected to {name}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to connect to {name}: {e}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python bluetooth_manager.py <gamepad_name>")
    else:
        connect_gamepad(sys.argv[1])
