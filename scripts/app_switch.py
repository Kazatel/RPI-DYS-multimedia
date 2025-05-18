#!/usr/bin/env python3
"""
Modified app_switch.py that can survive desktop environment termination
"""

import os
import sys
import subprocess
import argparse
import getpass
import time

# Simple print function for logging
def log_info(message):
    print(f"INFO: {message}")
    # Also log to a file for debugging desktop launches
    with open("/tmp/app_switch_log.txt", "a") as f:
        f.write(f"INFO: {message}\n")

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)
    # Also log to a file for debugging desktop launches
    with open("/tmp/app_switch_log.txt", "a") as f:
        f.write(f"ERROR: {message}\n")

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the service_manager.sh script in the same directory
SERVICE_MANAGER_SCRIPT = os.path.join(SCRIPT_DIR, "service_manager.sh")

# Default user (current user)
DEFAULT_USER = getpass.getuser()

# Map of app names to service names
APP_TO_SERVICE = {
    "kodi": "kodi",
    "retropie": "emulationstation",
    "emulationstation": "emulationstation",
    "desktop": "desktop"
}

def run_as_user(command, user=None):
    """
    Run a command as a specific user

    Args:
        command: The command to run (list or string)
        user: The user to run as (None for current user, 'root' for sudo without user)

    Returns:
        subprocess.CompletedProcess: The result of the command
    """
    if user is None or user == os.getenv("USER"):
        # Run as current user
        if isinstance(command, list):
            return subprocess.run(command)
        else:
            return subprocess.run(command, shell=True)
    elif user == "root":
        # Run with sudo (as root) without specifying a user
        if isinstance(command, list):
            sudo_cmd = ["sudo"] + command
            return subprocess.run(sudo_cmd)
        else:
            sudo_cmd = f"sudo {command}"
            return subprocess.run(sudo_cmd, shell=True)
    else:
        # Run as different user using sudo -u
        if isinstance(command, list):
            sudo_cmd = ["sudo", "-u", user] + command
            return subprocess.run(sudo_cmd)
        else:
            sudo_cmd = f"sudo -u {user} {command}"
            return subprocess.run(sudo_cmd, shell=True)

def kill_service(service):
    """
    Kill a service

    Args:
        service: The service to kill (kodi, emulationstation, desktop)

    Returns:
        bool: True if successful, False otherwise
    """
    log_info(f"Killing {service}...")

    # Determine which user should run the kill command
    if service == "desktop":
        # Desktop needs to be killed with sudo
        user = "root"
    else:
        # Other services can be killed as the normal user
        user = DEFAULT_USER

    try:
        result = run_as_user([SERVICE_MANAGER_SCRIPT, "kill", service], user)
        if result.returncode == 0:
            log_info(f"Successfully killed {service}")
            return True
        else:
            log_error(f"Failed to kill {service} (exit code {result.returncode})")
            return False
    except Exception as e:
        log_error(f"Error killing {service}: {e}")
        return False

def start_service(service):
    """
    Start a service

    Args:
        service: The service to start (kodi, emulationstation, desktop)

    Returns:
        bool: True if successful, False otherwise
    """
    log_info(f"Starting {service}...")

    # Determine which user should run the start command
    if service == "desktop":
        # Desktop needs to be started with sudo
        user = "root"
    else:
        # Other services can be started as the normal user
        user = DEFAULT_USER

    try:
        result = run_as_user([SERVICE_MANAGER_SCRIPT, "start", service], user)
        if result.returncode == 0:
            log_info(f"Successfully started {service}")
            return True
        else:
            log_error(f"Failed to start {service} (exit code {result.returncode})")
            return False
    except Exception as e:
        log_error(f"Error starting {service}: {e}")
        return False

def switch_to_app(app):
    """
    Switch to a specific application by killing others and starting the requested one

    Args:
        app: The application to switch to (kodi, retropie, emulationstation, desktop)

    Returns:
        bool: True if successful, False otherwise
    """
    # Map app name to service name
    if app not in APP_TO_SERVICE:
        log_error(f"Unknown application: {app}")
        log_info(f"Valid options are: {', '.join(APP_TO_SERVICE.keys())}")
        return False

    service = APP_TO_SERVICE[app]
    log_info(f"Switching to {app} (service: {service})...")

    # Map of services to kill for each service
    services_to_kill = {
        "kodi": ["emulationstation", "desktop"],
        "emulationstation": ["kodi", "desktop"],
        "desktop": ["kodi", "emulationstation"]
    }

    # Validate the service
    if service not in services_to_kill:
        log_error(f"Unknown service: {service}")
        return False

    # Get list of services to kill
    to_kill = services_to_kill[service]
    
    # Special handling for desktop - fork before killing desktop
    if "desktop" in to_kill:
        log_info("Desktop needs to be killed - forking to survive desktop termination")
        # Fork the process if we're killing the desktop
        if os.fork() != 0:
            # Parent process just exits successfully
            log_info("Parent process exiting, child will continue...")
            return True
        
        # Child process continues after a brief pause to ensure parent is gone
        time.sleep(1)
        log_info("Child process continuing after fork...")

    # Kill other services
    for other_service in to_kill:
        kill_service(other_service)

    # Start the requested service
    return start_service(service)

def main():
    """Main entry point"""
    # Write a timestamp to the log
    with open("/tmp/app_switch_log.txt", "a") as f:
        f.write(f"\n--- New app_switch.py run at {time.ctime()} ---\n")
        f.write(f"Args: {sys.argv}\n")
        f.write(f"User: {DEFAULT_USER}\n")
        f.write(f"Working directory: {os.getcwd()}\n")
    
    # Check for legacy usage pattern (app name as first argument)
    if len(sys.argv) == 2 and sys.argv[1] in APP_TO_SERVICE:
        # Legacy usage: python app_switch.py kodi
        return 0 if switch_to_app(sys.argv[1]) else 1

    parser = argparse.ArgumentParser(description="App Switching - Control application services")

    # Add app argument for direct app switching
    parser.add_argument("app", nargs="?", help="Application to switch to (kodi, retropie, emulationstation, desktop)")

    # Add subcommands for more advanced usage
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Kill command
    kill_parser = subparsers.add_parser("kill", help="Kill a service")
    kill_parser.add_argument("service", choices=["kodi", "emulationstation", "desktop"],
                          help="Service to kill")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a service")
    start_parser.add_argument("service", choices=["kodi", "emulationstation", "desktop"],
                           help="Service to start")

    # Switch command
    switch_parser = subparsers.add_parser("switch", help="Switch to an application")
    switch_parser.add_argument("app", choices=list(APP_TO_SERVICE.keys()),
                            help="Application to switch to")

    args = parser.parse_args()

    # Check if the service_manager.sh script exists
    if not os.path.exists(SERVICE_MANAGER_SCRIPT):
        log_error(f"Service manager script not found at {SERVICE_MANAGER_SCRIPT}")
        return 1

    # Make sure the script is executable
    os.chmod(SERVICE_MANAGER_SCRIPT, 0o755)

    # Process commands
    if args.command == "kill":
        success = kill_service(args.service)
    elif args.command == "start":
        success = start_service(args.service)
    elif args.command == "switch":
        success = switch_to_app(args.app)
    elif args.app:
        # Direct app switching (no subcommand)
        success = switch_to_app(args.app)
    else:
        parser.print_help()
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())