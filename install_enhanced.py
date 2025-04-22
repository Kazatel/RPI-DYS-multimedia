#!/usr/bin/env python3
"""
RPi-DYS-Multimedia Setup
A comprehensive installer for Raspberry Pi multimedia center
"""

import argparse
import importlib
import sys
import os
import subprocess
import config
from utils.logger import logger_instance as log
from utils.os_utils import (
    get_raspberry_pi_model,
    get_codename,
    is_running_as_root,
    reboot_countdown
)
from utils.config_validator import validate_config
from utils.error_handler import handle_error, try_operation
from utils.exceptions import ConfigurationError, SystemError
from modules.system_configuration import (
    apply_locale_settings,
    apply_boot_config,
    create_or_overwrite_bash_aliases
)
from modules.fstab_configurator import update_fstab_with_disks


# --- PRECHECK ---
def check_root():
    """Check if script is running as root"""
    if not is_running_as_root():
        print("❌ This script must be run with sudo.")
        print("👉 Please rerun with:\n")
        print("   sudo python install.py\n")
        sys.exit(1)


@handle_error(exit_on_error=True)
def ensure_supported_pi_environment():
    """Check if the current environment is supported"""
    os_codename = get_codename()
    pi_model = get_raspberry_pi_model()

    with log.log_section("Environment Check"):
        log.info(f"🔍 Detected OS codename: {os_codename}")
        log.info(f"🔍 Detected Raspberry Pi model: {pi_model}")

        os_supported = os_codename in config.TESTED_OS_VERSION
        model_supported = pi_model in config.TESTED_MODELS

        if os_supported and model_supported:
            log.info("✅ OS version and Raspberry Pi model are officially supported.")
        else:
            log.warning("⚠️ One or more components are not officially supported:")
            if not os_supported:
                log.warning(f"   - OS '{os_codename}' is not in TESTED_OS_VERSION: {config.TESTED_OS_VERSION}")
            if not model_supported:
                log.warning(f"   - Pi model '{pi_model}' is not in TESTED_MODELS: {config.TESTED_MODELS}")

            if config.ON_OWN_RISK:
                log.warning("⚠️ Proceeding at your own risk (ON_OWN_RISK is enabled).")
            else:
                raise SystemError("Unsupported environment and ON_OWN_RISK is disabled.")


# --- SYSTEM SETUP ---
@handle_error(exit_on_error=False)
def system_setup():
    """Run system configuration steps"""
    ensure_supported_pi_environment()
    
    with log.log_section("System Configuration"):
        log.info("⚙️ Applying system configurations...")
        
        with try_operation("Applying boot configuration"):
            apply_boot_config()
            
        with try_operation("Creating bash aliases"):
            create_or_overwrite_bash_aliases()
            
        with try_operation("Updating fstab"):
            update_fstab_with_disks()
            
        # Optional depending on setup
        # with try_operation("Applying locale settings"):
        #     apply_locale_settings()
            
        log.info("✅ System configuration complete.")
        
    reboot_countdown(10)


# --- APPLICATION INSTALLATION ---
MODULES_DIR = "modules"


@handle_error(exit_on_error=False)
def install_selected_apps(force_apps=None):
    """
    Install selected applications
    
    Args:
        force_apps: List of app names to force install, or None to use config
    """
    with log.log_section("Application Installation"):
        log.info("📦 Installing selected applications...")

        for app_name, app_config in config.APPLICATIONS.items():
            should_install = app_config.get("enabled", False)
            user = app_config.get("user", "root")

            if (force_apps and app_name in force_apps) or (not force_apps and should_install):
                try:
                    module_path = f"{MODULES_DIR}.{app_name}_install"
                    module = importlib.import_module(module_path)

                    with log.log_section(f"Installing {app_name.upper()}"):
                        log.info(f"🚀 Starting installation for: {app_name.upper()} (user: {user})")
                        
                        if hasattr(module, "main_install"):
                            module.main_install()
                        else:
                            log.warning(f"⚠️ No main_install() function found in {module_path}.")
                except ModuleNotFoundError as e:
                    log.error(f"❌ Module not found for {app_name}: {e}")
                except Exception as e:
                    log.log_exception(e, f"Error installing {app_name}")


@handle_error(exit_on_error=False)
def configure_selected_apps(force_apps=None):
    """
    Configure selected applications
    
    Args:
        force_apps: List of app names to force configure, or None to use config
    """
    with log.log_section("Application Configuration"):
        log.info("🔧 Configuring selected applications...")

        for app_name, app_config in config.APPLICATIONS.items():
            should_configure = app_config.get("enabled", False)
            user = app_config.get("user", "root")

            if (force_apps and app_name in force_apps) or (not force_apps and should_configure):
                try:
                    module_path = f"{MODULES_DIR}.{app_name}_install"
                    module = importlib.import_module(module_path)

                    with log.log_section(f"Configuring {app_name.upper()}"):
                        log.info(f"🔧 Running configuration for: {app_name.upper()} (user: {user})")

                        if hasattr(module, "main_configure"):
                            module.main_configure()
                        else:
                            log.warning(f"⚠️ No main_configure() function found in {module_path}.")
                except ModuleNotFoundError as e:
                    log.error(f"❌ Module not found for {app_name}: {e}")
                except Exception as e:
                    log.log_exception(e, f"Error configuring {app_name}")


# --- BLUETOOTH MANAGEMENT ---
@handle_error(exit_on_error=False)
def launch_bluetooth_manager(action="list", gamepad=None):
    """
    Launch the Bluetooth manager
    
    Args:
        action: Action to perform (list, pair, connect, status)
        gamepad: Gamepad name for connect/status actions
    """
    with log.log_section("Bluetooth Manager"):
        cmd = ["python", "scripts/bluetooth_manager.py", action]
        
        if gamepad and action in ["connect", "status"]:
            cmd.append(gamepad)
            
        log.info(f"🎮 Launching Bluetooth manager: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True)
            
            if action == "list":
                # After listing, ask if user wants to pair or connect
                choice = input("\n👉 Do you want to (p)air a new device, (c)onnect an existing one, or (q)uit? ").lower().strip()
                
                if choice.startswith('p'):
                    subprocess.run(["python", "scripts/bluetooth_manager.py", "pair"], check=True)
                elif choice.startswith('c'):
                    gamepad_name = input("👉 Enter the name of the gamepad to connect: ").strip()
                    if gamepad_name:
                        subprocess.run(["python", "scripts/bluetooth_manager.py", "connect", gamepad_name], check=True)
            
            log.info("✅ Bluetooth manager completed successfully.")
        except subprocess.CalledProcessError as e:
            log.error(f"❌ Bluetooth manager failed with return code {e.returncode}")
        except Exception as e:
            log.log_exception(e, "Error running Bluetooth manager")


# --- MENUS ---
def print_main_menu():
    """Print the main menu options"""
    print("\n=== Raspberry Pi Setup Assistant ===\n")
    print("Please select the setup phase you'd like to run:\n")
    print("1) 🛠 System Configuration")
    print("   - Sets locale, aliases, fstab, boot config")
    print("   - ⚠ Requires reboot after completion")
    print("2) 📦 Application Installation")
    print("   - Installs Kodi, RetroPie, Moonlight (based on config)")
    print("   - 🔄 Run installed apps once before next step")
    print("3) 🔧 Post-Install Configuration")
    print("   - Symlinks BIOS/ROMs, applies tweaks")
    print("4) 🎮 Bluetooth Gamepad Manager")
    print("   - Pair, connect, and manage Bluetooth gamepads")
    print("5) ⚙️  Advanced Mode")
    print("   - Run individual steps manually (no validation)")
    print("6) ❌ Exit")


def main_menu_loop():
    """Interactive main menu loop"""
    while True:
        print_main_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        if choice == "1":
            system_setup()
        elif choice == "2":
            install_selected_apps()
        elif choice == "3":
            configure_selected_apps()
        elif choice == "4":
            launch_bluetooth_manager()
        elif choice == "5":
            advanced_menu_loop()
        elif choice == "6":
            print("👋 Exiting installer.")
            sys.exit(0)
        else:
            print("❌ Invalid option. Please choose 1–6.")


def advanced_menu_loop():
    """Interactive advanced menu loop"""
    while True:
        print("\n=== Advanced Options ===")
        print("1) Apply locale settings")
        print("2) Update /etc/fstab")
        print("3) Apply boot config")
        print("4) Create bash aliases")
        print("5) Install Kodi")
        print("6) Install RetroPie")
        print("7) Install Moonlight")
        print("8) Run RetroPie post-config")
        print("9) Bluetooth gamepad operations")
        print("0) 🔙 Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            apply_locale_settings()
        elif choice == "2":
            update_fstab_with_disks()
        elif choice == "3":
            apply_boot_config()
        elif choice == "4":
            create_or_overwrite_bash_aliases()
        elif choice == "5":
            install_selected_apps(force_apps=["kodi"])
        elif choice == "6":
            install_selected_apps(force_apps=["retropie"])
        elif choice == "7":
            install_selected_apps(force_apps=["moonlight"])
        elif choice == "8":
            configure_selected_apps()
        elif choice == "9":
            bluetooth_submenu()
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")


def bluetooth_submenu():
    """Interactive Bluetooth submenu"""
    while True:
        print("\n=== Bluetooth Options ===")
        print("1) List paired gamepads")
        print("2) Pair new gamepad")
        print("3) Connect gamepad")
        print("4) Check gamepad status")
        print("0) 🔙 Back to Advanced Menu")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            launch_bluetooth_manager("list")
        elif choice == "2":
            launch_bluetooth_manager("pair")
        elif choice == "3":
            gamepad = input("👉 Enter gamepad name: ").strip()
            if gamepad:
                launch_bluetooth_manager("connect", gamepad)
        elif choice == "4":
            gamepad = input("👉 Enter gamepad name: ").strip()
            if gamepad:
                launch_bluetooth_manager("status", gamepad)
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Raspberry Pi DYS Multimedia Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python install.py                     # Run in interactive mode
  sudo python install.py system              # Run system configuration
  sudo python install.py apps                # Install all enabled applications
  sudo python install.py apps --app=kodi     # Install only Kodi
  sudo python install.py config              # Configure all enabled applications
  sudo python install.py bluetooth pair      # Run Bluetooth pairing mode
        """
    )
    
    # Add subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # System configuration
    system_parser = subparsers.add_parser("system", help="Run system configuration")
    
    # App installation
    apps_parser = subparsers.add_parser("apps", help="Install applications")
    apps_parser.add_argument("--app", choices=["kodi", "retropie", "moonlight"], 
                          help="Specific app to install (default: all enabled)")
    
    # Configuration
    config_parser = subparsers.add_parser("config", help="Configure applications")
    config_parser.add_argument("--app", choices=["kodi", "retropie", "moonlight"], 
                            help="Specific app to configure (default: all enabled)")
    
    # Bluetooth
    bluetooth_parser = subparsers.add_parser("bluetooth", help="Manage Bluetooth gamepads")
    bluetooth_parser.add_argument("action", choices=["list", "pair", "connect", "status"], 
                               help="Bluetooth action to perform")
    bluetooth_parser.add_argument("gamepad", nargs="?", help="Gamepad name (for connect/status)")
    
    # Validate
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    
    # Interactive mode (default)
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode")
    
    return parser.parse_args()


def main():
    """Main entry point"""
    # Check if running as root
    check_root()
    
    # Parse command line arguments
    args = parse_args()
    
    # Validate configuration
    try:
        validate_config(config)
    except ConfigurationError as e:
        log.error(f"Configuration validation failed: {e}")
        sys.exit(1)
    
    # Process commands
    if args.command == "system":
        system_setup()
    elif args.command == "apps":
        if args.app:
            install_selected_apps(force_apps=[args.app])
        else:
            install_selected_apps()
    elif args.command == "config":
        if args.app:
            configure_selected_apps(force_apps=[args.app])
        else:
            configure_selected_apps()
    elif args.command == "bluetooth":
        launch_bluetooth_manager(args.action, args.gamepad)
    elif args.command == "validate":
        log.info("✅ Configuration validation passed.")
    else:
        # Default to interactive mode
        main_menu_loop()


if __name__ == "__main__":
    main()
