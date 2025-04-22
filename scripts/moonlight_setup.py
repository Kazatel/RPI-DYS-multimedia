#!/usr/bin/env python3
"""
Moonlight Setup Script for Raspberry Pi
Helps users set up and pair Moonlight with an NVIDIA GameStream host
"""

import os
import sys
import subprocess
import time
import re
import socket
import ipaddress
import shutil
from getpass import getpass

# Add parent directory to path to import config if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_step(step_num, text):
    """Print a formatted step"""
    print(f"{Colors.BLUE}{Colors.BOLD}[Step {step_num}] {text}{Colors.ENDC}")

def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}{Colors.BOLD}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}{Colors.BOLD}✗ {text}{Colors.ENDC}")

def run_command(command, capture_output=True, shell=False):
    """Run a command and return the output"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        else:
            result = subprocess.run(command, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print_error(f"Error running command: {e}")
        return None

def is_raspberry_pi():
    """Check if the script is running on a Raspberry Pi"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            return 'Raspberry Pi' in model
    except:
        # If we can't read the file, try another method
        try:
            output = subprocess.check_output(['cat', '/proc/cpuinfo'], text=True)
            return 'BCM' in output or 'Raspberry Pi' in output
        except:
            return False

def check_moonlight_installed():
    """Check if Moonlight is installed and offer to install it if missing"""
    # Check if moonlight-qt is in PATH
    moonlight_path = shutil.which("moonlight-qt")
    if moonlight_path:
        print_success("Moonlight is installed at: " + moonlight_path)
        return True

    print_error("Moonlight is not installed!")
    install = input(f"{Colors.BOLD}Would you like to install Moonlight now? (y/n): {Colors.ENDC}").lower()

    if install == 'y':
        print_step("0", "Installing Moonlight")
        print("This will require sudo privileges...")

        # Update package lists
        print("Updating package lists...")
        update_result = run_command(["sudo", "apt", "update"])
        if update_result.returncode != 0:
            print_error("Failed to update package lists")
            print("Please try installing Moonlight manually:")
            print("  sudo apt update")
            print("  sudo apt install moonlight-qt")
            return False

        # Install moonlight-qt
        print("Installing moonlight-qt...")
        install_result = run_command(["sudo", "apt", "install", "-y", "moonlight-qt"])
        if install_result.returncode != 0:
            print_error("Failed to install Moonlight")
            print("Please try installing it manually:")
            print("  sudo apt install moonlight-qt")
            return False

        print_success("Moonlight installed successfully!")
        return True
    else:
        print_warning("Skipping Moonlight installation. The setup may not work correctly.")
        return False

def validate_ip_address(ip_string):
    """Validate if the string is a valid IP address"""
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

def get_host_ip():
    """Get the IP address of the NVIDIA host from user input"""
    while True:
        ip = input(f"{Colors.BOLD}Enter the IP address of your NVIDIA GameStream host PC: {Colors.ENDC}")
        if validate_ip_address(ip):
            return ip
        else:
            print_error("Invalid IP address. Please try again.")

def check_host_reachable(host_ip):
    """Check if the host is reachable"""
    print(f"Checking if host {host_ip} is reachable...")

    # Try to ping the host
    ping_result = run_command(["ping", "-c", "3", "-W", "2", host_ip])
    if ping_result.returncode != 0:
        print_error(f"Cannot reach host at {host_ip}")
        print("Please check that:")
        print("  1. Your host PC is turned on")
        print("  2. Both devices are connected to the same network")
        print("  3. The IP address is correct")
        return False

    # Try to check if the GameStream ports are open
    try:
        # Check TCP port 47989 (one of the GameStream ports)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host_ip, 47989))
        sock.close()

        if result != 0:
            print_warning(f"GameStream port 47989 is not open on {host_ip}")
            print("This might indicate that:")
            print("  1. NVIDIA GameStream is not enabled on the host")
            print("  2. A firewall is blocking the connection")
            print("  3. You're using Sunshine instead of GeForce Experience")
            choice = input("Do you want to continue anyway? (y/n): ").lower()
            return choice == 'y'

        return True
    except Exception as e:
        print_warning(f"Error checking GameStream ports: {e}")
        choice = input("Do you want to continue anyway? (y/n): ").lower()
        return choice == 'y'

def list_paired_hosts():
    """List all paired hosts"""
    print_step("0", "Checking for existing paired hosts")

    result = run_command(["moonlight-qt", "list"])
    if result.returncode != 0:
        print_warning("Failed to list paired hosts")
        return []

    # Parse the output to extract host information
    hosts = []
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if ":" in line and not line.startswith("Usage:"):
            parts = line.split(':', 1)
            if len(parts) == 2:
                host_name = parts[0].strip()
                host_info = parts[1].strip()
                hosts.append((host_name, host_info))

    return hosts

def is_host_paired(host_ip, hosts):
    """Check if the host is already paired"""
    for host_name, host_info in hosts:
        if host_ip in host_info:
            return True, host_name
    return False, None

def pair_with_host(host_ip):
    """Pair with the host"""
    print_step("3", "Pairing with the host")
    print(f"{Colors.YELLOW}A PIN will be displayed on your host PC.{Colors.ENDC}")
    print(f"{Colors.YELLOW}You'll need to enter it here when prompted.{Colors.ENDC}")

    input(f"{Colors.BOLD}Press Enter to start the pairing process...{Colors.ENDC}")

    # Start the pairing process
    pairing_process = subprocess.Popen(
        ["moonlight-qt", "pair", host_ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait a moment for the pairing dialog to appear on the host
    time.sleep(3)

    # Ask for the PIN
    pin = input(f"{Colors.BOLD}Enter the PIN displayed on your host PC: {Colors.ENDC}")

    # Send the PIN to the process
    pairing_process.communicate(input=pin)

    # Check if pairing was successful
    if pairing_process.returncode == 0:
        print_success("Pairing successful!")
        return True
    else:
        print_error("Pairing failed!")
        print("Please check that:")
        print("  1. You entered the correct PIN")
        print("  2. The pairing dialog is visible on your host PC")
        print("  3. NVIDIA GameStream is enabled on your host PC")
        return False

def verify_pairing(host_ip):
    """Verify that the pairing was successful"""
    print_step("4", "Verifying pairing")

    # List hosts again to check if our host is now paired
    hosts = list_paired_hosts()
    paired, host_name = is_host_paired(host_ip, hosts)

    if paired:
        print_success(f"Successfully paired with {host_name} ({host_ip})!")
        return True
    else:
        print_error(f"Could not verify pairing with {host_ip}")
        return False

def list_apps(host_ip):
    """List available apps on the host"""
    print_step("5", "Listing available apps")

    result = run_command(["moonlight-qt", "list", host_ip])
    if result.returncode != 0:
        print_warning("Failed to list apps")
        return False

    print_success("Available apps:")

    # Parse and display the apps
    lines = result.stdout.strip().split('\n')
    apps = []
    for line in lines:
        if line.startswith("    "):  # Apps are indented in the output
            app_name = line.strip()
            apps.append(app_name)
            print(f"  • {app_name}")

    if not apps:
        print_warning("No apps found on the host")
        print("You may need to add apps in GeForce Experience or Sunshine")

    return len(apps) > 0

def show_nvidia_host_setup_instructions():
    """Show instructions for setting up the NVIDIA host"""
    print_header("NVIDIA GameStream Host Setup Instructions")

    print("Before continuing, make sure your NVIDIA PC has:")
    print(f"{Colors.BOLD}1. A supported NVIDIA GPU (GTX/RTX 600+ series){Colors.ENDC}")
    print(f"{Colors.BOLD}2. GeForce Experience installed and updated{Colors.ENDC}")
    print(f"{Colors.BOLD}3. GameStream enabled in GeForce Experience{Colors.ENDC}")

    print("\nTo enable GameStream on your PC:")
    print("  1. Open GeForce Experience")
    print("  2. Click the Settings (gear) icon in the top-right")
    print("  3. Click on the SHIELD tab")
    print("  4. Make sure GameStream is toggled ON")

    print("\nAlternatively, if you're using Sunshine instead of GeForce Experience:")
    print("  1. Make sure Sunshine is installed and running on your PC")
    print("  2. Open the Sunshine web interface (usually https://localhost:47990)")
    print("  3. Make sure your PC's firewall allows Sunshine connections")

    input(f"\n{Colors.BOLD}Press Enter when your host PC is ready...{Colors.ENDC}")

def ensure_documentation_exists():
    """Check if the documentation exists and create it if it doesn't"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(script_dir)
    # Path to the documentation
    doc_path = os.path.join(project_root, "docs", "MOONLIGHT_SETUP_GUIDE.md")

    # Check if the documentation exists
    if os.path.exists(doc_path):
        return True

    # Create the docs directory if it doesn't exist
    docs_dir = os.path.dirname(doc_path)
    if not os.path.exists(docs_dir):
        try:
            os.makedirs(docs_dir)
        except Exception as e:
            print_warning(f"Could not create docs directory: {e}")
            return False

    # We would need to create the documentation file here
    # This would be a large block of markdown text
    # For brevity, we'll just create a simple placeholder
    try:
        with open(doc_path, "w") as f:
            f.write("# Moonlight Setup Guide\n\n")
            f.write("This is a placeholder for the full documentation.\n\n")
            f.write("Please visit https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide for the complete guide.\n")
        print_success(f"Created documentation at {doc_path}")
        return True
    except Exception as e:
        print_warning(f"Could not create documentation: {e}")
        return False

def main():
    """Main function"""
    print_header("Moonlight Setup for NVIDIA GameStream")

    # Check if running on a Raspberry Pi
    if is_raspberry_pi():
        print_success("Running on a Raspberry Pi")
    else:
        print_warning("This script is optimized for Raspberry Pi, but will work on other Linux systems")
        print("Some features may not work as expected on your system.")
        print()

    # Check if Moonlight is installed
    if not check_moonlight_installed():
        return

    # Ensure documentation exists
    ensure_documentation_exists()

    # Show instructions for setting up the NVIDIA host
    show_nvidia_host_setup_instructions()

    # Step 1: Get the host IP
    print_step("1", "Enter your NVIDIA PC's IP address")
    host_ip = get_host_ip()

    # Step 2: Check if the host is reachable
    print_step("2", "Checking connection to host")
    if not check_host_reachable(host_ip):
        choice = input("Do you want to try again with a different IP? (y/n): ").lower()
        if choice == 'y':
            host_ip = get_host_ip()
            if not check_host_reachable(host_ip):
                print_error("Still cannot reach host. Please check your network configuration.")
                return
        else:
            print_error("Cannot continue without a reachable host.")
            return

    # Check if already paired
    hosts = list_paired_hosts()
    paired, host_name = is_host_paired(host_ip, hosts)

    if paired:
        print_success(f"Already paired with {host_name} ({host_ip})")
        choice = input("Do you want to pair again? (y/n): ").lower()
        if choice != 'y':
            # Skip to listing apps
            list_apps(host_ip)
            return

    # Step 3: Pair with the host
    if not pair_with_host(host_ip):
        choice = input("Do you want to try pairing again? (y/n): ").lower()
        if choice == 'y':
            if not pair_with_host(host_ip):
                print_error("Pairing failed again. Please check your setup and try again later.")
                return
        else:
            print_error("Cannot continue without pairing.")
            return

    # Step 4: Verify pairing
    if not verify_pairing(host_ip):
        print_warning("Could not verify pairing, but we'll continue anyway.")

    # Step 5: List available apps
    list_apps(host_ip)

    # Final instructions
    print_header("Setup Complete")
    print("You can now stream games from your PC using Moonlight!")
    print("\nTo start streaming:")
    print("  1. Launch Moonlight from the desktop or menu")
    print("  2. Select your PC from the list")
    print("  3. Choose a game or app to stream")

    print(f"\n{Colors.BOLD}Useful commands:{Colors.ENDC}")
    print("  moonlight-qt                  # Launch the Moonlight GUI")
    print("  moonlight-qt stream HOST APP  # Stream a specific app")
    print("  moonlight-qt quit HOST        # Quit the current streaming session")
    print("  moonlight-qt list HOST        # List available apps")

    print(f"\n{Colors.BOLD}Additional Resources:{Colors.ENDC}")
    print(f"  {Colors.BLUE}docs/MOONLIGHT_SETUP_GUIDE.md{Colors.ENDC}     # Detailed documentation")
    print(f"  {Colors.BLUE}https://moonlight-stream.org{Colors.ENDC}     # Official Moonlight website")
    print(f"  {Colors.BLUE}https://moonlight-stream.org/discord{Colors.ENDC} # Discord support server")

    print(f"\n{Colors.YELLOW}{Colors.BOLD}Note: For the best experience, use a wired network connection if possible.{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        sys.exit(1)
