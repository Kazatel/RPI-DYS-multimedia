#!/usr/bin/env python3
"""
Service Manager - Python wrapper for service_manager.sh
Controls which user runs which tasks for application switching
This script is designed to be independent of the project structure
"""

import os
import sys
import subprocess
import argparse
import getpass

# Simple print function for logging
def log_info(message):
    print(f"INFO: {message}")

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the service_manager.sh script in the same directory
SERVICE_MANAGER_SCRIPT = os.path.join(SCRIPT_DIR, "service_manager.sh")

# Default user (current user)
DEFAULT_USER = getpass.getuser()

def run_as_user(command, user=None):
    """
    Run a command as a specific user

    Args:
        command: The command to run (list or string)
        user: The user to run as (None for current user)

    Returns:
        subprocess.CompletedProcess: The result of the command
    """
    if user is None or user == os.getenv("USER"):
        # Run as current user
        if isinstance(command, list):
            return subprocess.run(command)
        else:
            return subprocess.run(command, shell=True)
    else:
        # Run as different user using sudo
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
        user = "DEFAULT_USER"
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
        app: The application to switch to (kodi, emulationstation, desktop)

    Returns:
        bool: True if successful, False otherwise
    """
    log_info(f"Switching to {app}...")

    # Map of services to kill for each app
    services_to_kill = {
        "kodi": ["emulationstation", "desktop"],
        "emulationstation": ["kodi", "desktop"],
        "desktop": ["kodi", "emulationstation"]
    }

    # Validate the app
    if app not in services_to_kill:
        log_error(f"Unknown application: {app}")
        log_info("Valid options are: kodi, emulationstation, desktop")
        return False

    # Kill other services
    for service in services_to_kill[app]:
        kill_service(service)

    # Start the requested app
    return start_service(app)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Service Manager - Control application services")
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
    switch_parser.add_argument("app", choices=["kodi", "emulationstation", "desktop"],
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
    else:
        parser.print_help()
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
