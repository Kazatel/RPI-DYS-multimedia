#!/usr/bin/env python3
"""
Bluetooth Manager for gamepad pairing
Handles timeouts and process control effectively when using bluetoothctl
"""

import subprocess
import time
import os
import sys
import re
import signal
import select

# Add parent directory to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


class BluetoothctlProcess:
    """Interactive bluetoothctl process wrapper with timeout control"""

    def __init__(self, timeout=30):
        self.process = None
        self.timeout = timeout
        self.output_buffer = ""

    def __enter__(self):
        """Start bluetoothctl process when entering context"""
        self.process = subprocess.Popen(
            ["bluetoothctl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up process when exiting context"""
        if self.process:
            try:
                self.send_command("exit")
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()

    def send_command(self, command, wait_for=None, timeout=None):
        """
        Send command to bluetoothctl and optionally wait for specific output

        Args:
            command: Command to send
            wait_for: String or regex pattern to wait for in output
            timeout: Custom timeout for this command (uses default if None)

        Returns:
            Collected output as string
        """
        if not self.process:
            raise RuntimeError("Process not started")

        # Use default timeout if not specified
        if timeout is None:
            timeout = self.timeout

        # Send command
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

        # If no wait condition, return immediately
        if not wait_for:
            return ""

        # Prepare regex pattern if wait_for is a string
        if isinstance(wait_for, str):
            pattern = re.compile(re.escape(wait_for))
        else:
            pattern = wait_for

        # Wait for output with timeout
        output = ""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if there's data to read with a small timeout
            ready, _, _ = select.select([self.process.stdout], [], [], 0.1)

            if ready:
                line = self.process.stdout.readline()
                if not line:  # EOF
                    break

                output += line
                print(f"  > {line.strip()}")

                # Check if we got what we're waiting for
                if pattern.search(line):
                    return output

        # If we get here, we timed out
        print(f"⚠️ Timeout waiting for: {wait_for}")
        return output

    def wait_for_pairing_success(self, mac, timeout=None):
        """
        Wait for successful pairing messages
        Returns True if successful, False otherwise
        """
        if timeout is None:
            timeout = self.timeout

        start_time = time.time()
        success_patterns = [
            re.compile(r"Pairing successful"),
            re.compile(r"Connection successful")
        ]

        while time.time() - start_time < timeout:
            ready, _, _ = select.select([self.process.stdout], [], [], 0.1)

            if ready:
                line = self.process.stdout.readline()
                if not line:  # EOF
                    break

                print(f"  > {line.strip()}")

                # Check for success patterns
                for pattern in success_patterns:
                    if pattern.search(line):
                        return True

                # Check for common failure patterns
                if "Failed to pair" in line or "Connection failed" in line:
                    return False

        # Timeout reached
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


def get_existing_devices():
    """Get list of already known devices before scanning"""
    try:
        output = subprocess.check_output(["bluetoothctl", "devices"], text=True)
        devices = {}
        for line in output.splitlines():
            match = re.search(r"Device ([\w:]+) (.+)", line)
            if match:
                mac, name = match.groups()
                devices[mac] = name
        return devices
    except subprocess.CalledProcessError:
        return {}


def discover_devices(scan_time=20):
    """
    Scan for Bluetooth devices with proper timeout handling
    Returns dict of MAC -> Name
    """
    print("🔍 Scanning for Bluetooth devices...")

    # Get existing devices before scanning
    existing_devices = get_existing_devices()
    if existing_devices:
        print("📋 Existing known devices before scanning:")
        for mac, name in existing_devices.items():
            print(f"  📱 Known: {name} ({mac})")

    # Initialize devices with existing ones
    devices = existing_devices.copy()

    # Track all lines for post-scan analysis
    all_output_lines = []

    with BluetoothctlProcess(timeout=scan_time+5) as bt:
        # Turn on scanning
        bt.send_command("power on")
        bt.send_command("scan on")

        # Wait for scan_time seconds
        print(f"⏳ Scanning for {scan_time} seconds...")
        start_time = time.time()

        while time.time() - start_time < scan_time:
            ready, _, _ = select.select([bt.process.stdout], [], [], 0.1)

            if ready:
                line = bt.process.stdout.readline()
                if not line:
                    break

                # Save all output for later analysis
                all_output_lines.append(line)

                # Look for device discoveries
                match = re.search(r"Device ([\w:]+) (.+)", line)
                if match:
                    mac, name = match.groups()
                    devices[mac] = name
                    print(f"  📱 Found: {name} ({mac})")

                # Also look for NEW device lines which might not have the Device prefix
                new_match = re.search(r"\[NEW\].+Device ([\w:]+) (.+)", line)
                if new_match:
                    mac, name = new_match.groups()
                    devices[mac] = name
                    print(f"  🆕 New device: {name} ({mac})")

            # Small sleep to prevent CPU hogging
            time.sleep(0.01)

        # Turn off scanning
        bt.send_command("scan off")

    # If no devices found during active scanning, try to extract from the output
    if not devices:
        print("⚠️ No devices found during active scanning, analyzing full output...")
        for line in all_output_lines:
            # Look for any MAC address patterns
            mac_match = re.search(r"((?:[0-9A-F]{2}:){5}[0-9A-F]{2})", line, re.IGNORECASE)
            if mac_match:
                mac = mac_match.group(1)
                name = "Unknown Device"
                # Try to extract a name if possible
                name_match = re.search(r"Device.+?(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\s+(.+)", line, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1)
                devices[mac] = name
                print(f"  🔍 Extracted: {name} ({mac})")

    # Get final list of devices after scanning
    final_devices = get_existing_devices()

    # Add any devices found in final check that weren't in our list
    for mac, name in final_devices.items():
        if mac not in devices:
            devices[mac] = name
            print(f"  ➕ Added from final check: {name} ({mac})")

    if not devices:
        print("❌ No devices found after scanning.")
    else:
        print(f"✅ Found {len(devices)} device(s) in total.")

    return devices


def pair_device(mac, timeout=30):
    """
    Attempt to pair/trust/connect a device by MAC with proper timeout handling
    Returns True if successful, False otherwise
    """
    print(f"\n🔗 Pairing with {mac}...")
    print("⏳ This may take some time. Please wait...")

    with BluetoothctlProcess(timeout=timeout) as bt:
        # Setup agent
        bt.send_command("power on")
        bt.send_command("agent on")
        bt.send_command("default-agent")

        # Start pairing
        print("📲 Sending pair command...")
        bt.send_command(f"pair {mac}")

        # Wait for pairing to complete
        pairing_success = bt.wait_for_pairing_success(mac, timeout=timeout)

        if not pairing_success:
            print("❌ Pairing failed or timed out")
            return False

        # Trust device
        print("🔒 Trusting device...")
        bt.send_command(f"trust {mac}")
        time.sleep(2)  # Give it time to process

        # Connect to device
        print("🔌 Connecting to device...")
        bt.send_command(f"connect {mac}")

        # Wait for connection to complete
        connection_success = bt.wait_for_pairing_success(mac, timeout=timeout)

        if not connection_success:
            print("⚠️ Connection may have failed")

    # Verify final status
    print("🔍 Verifying connection status...")
    time.sleep(3)  # Give system time to update status
    paired, trusted, connected = check_device_status(mac)

    print(f"\n🔎 Final Status:")
    print(f"   Paired:    {paired}")
    print(f"   Trusted:   {trusted}")
    print(f"   Connected: {connected}")

    return paired and trusted and connected


def connect_gamepad(name, timeout=30):
    """
    Connect a gamepad from config with proper timeout handling
    Returns True if successful, False otherwise
    """
    mac = config.GAMEPADS.get(name)
    if not mac:
        print(f"❌ Gamepad '{name}' not found in config.")
        return False

    print(f"🎮 Connecting to gamepad '{name}' ({mac})...")

    # Check current status first
    paired, trusted, connected = check_device_status(mac)

    if connected:
        print(f"✅ Gamepad '{name}' is already connected!")
        return True

    if paired and trusted:
        print(f"ℹ️ Gamepad is paired and trusted, attempting to connect...")
        with BluetoothctlProcess(timeout=timeout) as bt:
            bt.send_command("power on")
            bt.send_command(f"connect {mac}")
            connection_success = bt.wait_for_pairing_success(mac, timeout=timeout)

        # Verify final status
        time.sleep(2)
        _, _, connected = check_device_status(mac)

        if connected:
            print(f"✅ Successfully connected to {name}.")
            return True
        else:
            print(f"⚠️ Connection failed. Attempting full pairing...")

    # If we get here, we need to do a full pairing
    return pair_device(mac, timeout=timeout)


def pick_device(devices):
    """Allow user to pick a device from scanned list."""
    print("\n📡 Found devices:")
    choices = list(devices.items())

    if not choices:
        print("❌ No devices found!")
        return None, None

    # Create a reverse lookup of MAC addresses to gamepad names from config
    config_gamepads_by_mac = {mac.upper(): name for name, mac in config.GAMEPADS.items()}

    for i, (mac, name) in enumerate(choices):
        # Check if this MAC address is in our config
        config_name = config_gamepads_by_mac.get(mac.upper(), "")
        config_info = f" [{config_name}]" if config_name else ""

        print(f"{i + 1}. {name} ({mac}){config_info}")

    try:
        choice = int(input("👉 Enter the number of the device to pair (or 0 to cancel): "))
        if choice == 0:
            return None, None
        return choices[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid selection")
        return None, None


def pair_mode(timeout=45):
    """Run interactive pairing flow with proper timeout handling."""
    devices = discover_devices()

    if not devices:
        print("❌ No devices found. Try again.")
        return False

    mac, name = pick_device(devices)
    if not mac:
        return False

    success = pair_device(mac, timeout=timeout)

    if success:
        print(f"✅ Successfully paired and connected to {name} ({mac})!")

        # Check if this device is already in config
        existing_name = None
        for name, config_mac in config.GAMEPADS.items():
            if config_mac.upper() == mac.upper():
                existing_name = name
                break

        if existing_name:
            print(f"\nℹ️ This gamepad is already in your config as '{existing_name}'")
        else:
            # Ask if user wants to save to config
            save = input("\n💾 Save this gamepad to config.py? (y/n): ").lower().strip()
            if save == 'y':
                gamepad_name = input("👉 Enter a name for this gamepad: ").strip()
                if gamepad_name:
                    print(f"\nTo save this gamepad, add the following to your config.py file:")
                    print(f"\nGAMEPADS = {{")

                    # Show existing gamepads
                    for name, config_mac in config.GAMEPADS.items():
                        print(f"    '{name}': '{config_mac}',")

                    # Show the new gamepad
                    print(f"    '{gamepad_name}': '{mac}',")
                    print(f"}}")
    else:
        print(f"❌ Failed to pair with {name} ({mac})")

    return success


def list_gamepads():
    """List all gamepads from config with their connection status"""
    if not config.GAMEPADS:
        print("❌ No gamepads configured in config.py")
        return

    print("🎮 Configured gamepads:")
    print("\nNAME\t\tMAC ADDRESS\t\tSTATUS")
    print("----\t\t-----------\t\t------")

    for name, mac in config.GAMEPADS.items():
        paired, trusted, connected = check_device_status(mac)

        status = "✅ Connected" if connected else "❌ Disconnected"
        if paired and trusted and not connected:
            status = "⚠️ Paired but not connected"
        elif not paired and not trusted:
            status = "❓ Unknown/Not paired"

        print(f"{name}\t\t{mac}\t\t{status}")


def usage():
    print("Usage:")
    print("  python bluetooth_manager.py pair")
    print("  python bluetooth_manager.py connect <gamepad_name>")
    print("  python bluetooth_manager.py status <gamepad_name>")
    print("  python bluetooth_manager.py list")
    print("\nAvailable gamepads:")
    for name in config.GAMEPADS:
        print(f"  - {name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    action = sys.argv[1]

    if action == "pair":
        success = pair_mode()
        sys.exit(0 if success else 1)
    elif action == "connect" and len(sys.argv) == 3:
        success = connect_gamepad(sys.argv[2])
        sys.exit(0 if success else 1)
    elif action == "status" and len(sys.argv) == 3:
        name = sys.argv[2]
        mac = config.GAMEPADS.get(name)
        if not mac:
            print(f"❌ Gamepad '{name}' not found in config.")
            sys.exit(1)
        paired, trusted, connected = check_device_status(mac)
        print(f"Status for gamepad '{name}' ({mac}):")
        print(f"   Paired:    {paired}")
        print(f"   Trusted:   {trusted}")
        print(f"   Connected: {connected}")
        sys.exit(0)
    elif action == "list":
        list_gamepads()
        sys.exit(0)
    else:
        usage()
        sys.exit(1)
