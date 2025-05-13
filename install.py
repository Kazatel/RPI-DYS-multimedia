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
from modules.system_configuration import (
    apply_locale_settings,
    apply_boot_config,
    create_or_overwrite_bash_aliases,
    update_environment_variable_menu
)
from modules.fstab_configurator import update_fstab_with_disks

# Import config validation if available
try:
    from utils.config_validator import validate_config
    CONFIG_VALIDATION_AVAILABLE = True
except ImportError:
    CONFIG_VALIDATION_AVAILABLE = False


# --- PRECHECK ---
if not is_running_as_root():
    print("❌ This script must be run with sudo.")
    print("👉 Please rerun with:\n")
    print("   sudo python install.py\n")
    sys.exit(1)


def ensure_supported_pi_environment():
    os_codename = get_codename()
    pi_model = get_raspberry_pi_model()

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
            log.error("❌ Aborting installation — unsupported environment and ON_OWN_RISK is disabled.")
            sys.exit(1)


# --- SYSTEM SETUP ---
def system_setup():
    ensure_supported_pi_environment()
    print("\n⚙️  Applying system configurations...")
    apply_boot_config()
    create_or_overwrite_bash_aliases()
    update_fstab_with_disks()
    # apply_locale_settings()  # Optional depending on setup
    reboot_countdown(10)


# --- APPLICATION INSTALLATION ---
MODULES_DIR = "modules"


def install_selected_apps(force_apps=None):
    print("\n📦 Installing selected applications...")

    for app_name, app_config in config.APPLICATIONS.items():
        should_install = app_config.get("enabled", False)
        user = app_config.get("user", "root")

        if force_apps or should_install:
            try:
                module_path = f"{MODULES_DIR}.{app_name}_install"
                module = importlib.import_module(module_path)

                print(f"\n🚀 Starting installation for: {app_name.upper()} (user: {user})")

                if hasattr(module, "main_install"):
                    module.main_install()
                else:
                    print(f"⚠️  No main_install() function found in {module_path}.")
            except ModuleNotFoundError as e:
                print(f"❌ Module not found for {app_name}: {e}")


def configure_selected_apps(force_apps=None):
    print("\n🔧 Configuring selected applications...")

    for app_name, app_config in config.APPLICATIONS.items():
        should_configure = app_config.get("enabled", False)
        user = app_config.get("user", "root")

        if force_apps or should_configure:
            try:
                # First try to import the dedicated config module
                config_module_path = f"{MODULES_DIR}.{app_name}_config"
                try:
                    config_module = importlib.import_module(config_module_path)
                    print(f"\n🔧 Running configuration for: {app_name.upper()} (user: {user})")

                    if hasattr(config_module, "main"):
                        config_module.main()
                    else:
                        print(f"⚠️  No main() function found in {config_module_path}.")
                except ModuleNotFoundError:
                    # Fall back to the install module if config module doesn't exist
                    install_module_path = f"{MODULES_DIR}.{app_name}_install"
                    install_module = importlib.import_module(install_module_path)

                    print(f"\n🔧 Running configuration for: {app_name.upper()} (user: {user})")
                    print(f"⚠️  Using legacy install module for configuration")

                    if hasattr(install_module, "main_configure"):
                        install_module.main_configure()
                    else:
                        print(f"⚠️  No main_configure() function found in {install_module_path}.")
            except ModuleNotFoundError as e:
                print(f"❌ Module not found for {app_name}: {e}")


# --- MENUS ---
def print_main_menu():
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
    print("4) 🔄 App Switching Setup")
    print("   - Configure switching between GUI applications")
    print("   - Sets up desktop shortcuts and boot options")
    print("5) 🎮 Bluetooth Gamepad Setup")
    print("   - Pair, connect, and manage Bluetooth gamepads")
    print("6) 🎮 Moonlight Streaming Setup")
    print("   - Configure Moonlight for NVIDIA GameStream")
    print("7) ⚙️  Advanced Mode")
    print("   - Run individual steps manually (no validation)")
    print("8) 🔄 Reboot System")
    print("   - Restart the Raspberry Pi")
    print("9) ❌ Exit")


def setup_app_switching():
    """Set up app switching between GUI applications"""
    try:
        from modules import app_switching
        app_switching.main_install()
    except ImportError as e:
        print(f"❌ Failed to import app_switching module: {e}")
        return False
    return True


def setup_bluetooth():
    """Set up Bluetooth gamepads"""
    try:
        bluetooth_submenu()
        return True
    except Exception as e:
        print(f"❌ Error during Bluetooth setup: {e}")
        return False


def bluetooth_submenu():
    """Interactive Bluetooth submenu"""
    while True:
        print("\n=== Bluetooth Gamepad Setup ===")
        print("1) List paired gamepads")
        print("2) Pair new gamepad")
        print("3) Connect gamepad")
        print("4) Check gamepad status")
        print("0) 🔙 Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            result = subprocess.run(["python", "scripts/bluetooth_manager.py", "list"], capture_output=True, text=True)
            print(result.stdout)

            # After listing, ask if user wants to pair or connect
            follow_up = input("\n👉 Do you want to (p)air a new device, (c)onnect an existing one, or (q)uit? ").lower().strip()
            if follow_up.startswith('p'):
                subprocess.run(["python", "scripts/bluetooth_manager.py", "pair"])
            elif follow_up.startswith('c'):
                gamepad_name = input("👉 Enter the name of the gamepad to connect: ").strip()
                if gamepad_name:
                    subprocess.run(["python", "scripts/bluetooth_manager.py", "connect", gamepad_name])
        elif choice == "2":
            subprocess.run(["python", "scripts/bluetooth_manager.py", "pair"])
        elif choice == "3":
            gamepad = input("👉 Enter gamepad name: ").strip()
            if gamepad:
                subprocess.run(["python", "scripts/bluetooth_manager.py", "connect", gamepad])
        elif choice == "4":
            gamepad = input("👉 Enter gamepad name: ").strip()
            if gamepad:
                subprocess.run(["python", "scripts/bluetooth_manager.py", "status", gamepad])
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")


def setup_moonlight():
    """Set up Moonlight streaming"""
    try:
        moonlight_submenu()
        return True
    except Exception as e:
        print(f"❌ Error during Moonlight setup: {e}")
        return False


def moonlight_submenu():
    """Interactive Moonlight submenu"""
    while True:
        print("\n=== Moonlight Streaming Setup ===")
        print("1) Install/Update Moonlight")
        print("2) Configure Moonlight")
        print("3) Launch Moonlight GUI")
        print("4) List paired PCs")
        print("5) Stream from a paired PC")
        print("0) 🔙 Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            try:
                from modules import moonlight_install
                moonlight_install.main_install()
                print("✅ Moonlight installation completed.")
            except ImportError as e:
                print(f"❌ Failed to import moonlight_install module: {e}")
            except Exception as e:
                print(f"❌ Error during Moonlight installation: {e}")
        elif choice == "2":
            try:
                # Try to use the dedicated config module first
                try:
                    from modules import moonlight_config
                    moonlight_config.main()
                    print("✅ Moonlight configuration completed.")
                except ImportError:
                    # Fall back to the install module if config module doesn't exist
                    from modules import moonlight_install
                    moonlight_install.main_configure()
                    print("✅ Moonlight configuration completed (using legacy module).")
            except ImportError as e:
                print(f"❌ Failed to import Moonlight module: {e}")
            except Exception as e:
                print(f"❌ Error during Moonlight configuration: {e}")
        elif choice == "3":
            try:
                subprocess.run(["moonlight-qt"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to launch Moonlight GUI: {e}")
            except FileNotFoundError:
                print("❌ Moonlight is not installed. Run the installation first.")
        elif choice == "4":
            try:
                subprocess.run(["moonlight-qt", "list"], check=True)
                input("\nPress Enter to continue...")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to list paired PCs: {e}")
            except FileNotFoundError:
                print("❌ Moonlight is not installed. Run the installation first.")
        elif choice == "5":
            host = input("👉 Enter the host PC name or IP: ").strip()
            if host:
                app = input("👉 Enter the app name to stream (or 'Desktop'): ").strip()
                if app:
                    try:
                        subprocess.run(["moonlight-qt", "stream", host, app], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Failed to stream: {e}")
                    except FileNotFoundError:
                        print("❌ Moonlight is not installed. Run the installation first.")
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")


def reboot_system():
    """Reboot the Raspberry Pi"""
    print("\n🔄 Preparing to reboot the system...")
    confirm = input("Are you sure you want to reboot? (y/n): ").strip().lower()
    if confirm == 'y' or confirm == 'yes':
        print("🔄 Rebooting now...")
        subprocess.run(["sudo", "reboot"])
    else:
        print("❌ Reboot cancelled.")

def main_menu_loop():
    while True:
        print_main_menu()
        choice = input("\nEnter your choice (1-9): ").strip()
        if choice == "1":
            system_setup()
        elif choice == "2":
            install_selected_apps()
        elif choice == "3":
            configure_selected_apps()
        elif choice == "4":
            setup_app_switching()
        elif choice == "5":
            setup_bluetooth()
        elif choice == "6":
            setup_moonlight()
        elif choice == "7":
            advanced_menu_loop()
        elif choice == "8":
            reboot_system()
        elif choice == "9":
            print("👋 Exiting installer.")
            sys.exit(0)
        else:
            print("❌ Invalid option. Please choose 1–9.")


def advanced_menu_loop():
    while True:
        print("\n=== Advanced Options ===")
        print("1) Apply locale settings")
        print("2) Update /etc/fstab")
        print("3) Apply boot config")
        print("4) Create bash aliases")
        print("5) Install Kodi")
        print("6) Install RetroPie")
        print("7) Install Moonlight")
        print("8) Configure applications")
        print("9) Set up app switching")
        print("10) Bluetooth gamepad setup")
        print("11) Moonlight streaming setup")
        print("12) Update DYS_RPI environment variable")
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
            setup_app_switching()
        elif choice == "10":
            setup_bluetooth()
        elif choice == "11":
            setup_moonlight()
        elif choice == "12":
            update_environment_variable_menu()
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
  sudo python install.py app-switching       # Set up app switching
  sudo python install.py bluetooth pair      # Run Bluetooth pairing mode
  sudo python install.py moonlight           # Set up Moonlight streaming
  sudo python install.py env-var             # Update DYS_RPI environment variable
  sudo python install.py env-var --path=/opt/rpi-dys  # Set custom path for DYS_RPI
  sudo python install.py reboot              # Reboot the system
        """
    )

    # Add subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # System configuration
    subparsers.add_parser("system", help="Run system configuration")

    # App installation
    apps_parser = subparsers.add_parser("apps", help="Install applications")
    apps_parser.add_argument("--app", choices=["kodi", "retropie", "moonlight"],
                          help="Specific app to install (default: all enabled)")

    # Configuration
    config_parser = subparsers.add_parser("config", help="Configure applications")
    config_parser.add_argument("--app", choices=["kodi", "retropie", "moonlight"],
                            help="Specific app to configure (default: all enabled)")

    # App switching
    subparsers.add_parser("app-switching", help="Set up app switching")

    # Bluetooth
    bluetooth_parser = subparsers.add_parser("bluetooth", help="Manage Bluetooth gamepads")
    bluetooth_parser.add_argument("action", choices=["list", "pair", "connect", "status"],
                               help="Bluetooth action to perform")
    bluetooth_parser.add_argument("gamepad", nargs="?", help="Gamepad name (for connect/status)")

    # Moonlight
    subparsers.add_parser("moonlight", help="Set up Moonlight streaming")

    # Environment variable
    env_parser = subparsers.add_parser("env-var", help="Update DYS_RPI environment variable")
    env_parser.add_argument("--path", help="Custom path to set for DYS_RPI (optional)")

    # Reboot
    subparsers.add_parser("reboot", help="Reboot the system")

    # Validate
    if CONFIG_VALIDATION_AVAILABLE:
        subparsers.add_parser("validate", help="Validate configuration")

    # Interactive mode (default)
    subparsers.add_parser("interactive", help="Run in interactive mode")

    return parser.parse_args()


def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_args()

    # Validate configuration if available
    if CONFIG_VALIDATION_AVAILABLE:
        try:
            validate_config(config)
            if args.command == "validate":
                print("✅ Configuration validation passed.")
                sys.exit(0)
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            if args.command == "validate":
                sys.exit(1)
            print("⚠️ Continuing despite validation errors...")

    # Process commands
    if args.command == "system":
        system_setup()
    elif args.command == "apps":
        if hasattr(args, 'app') and args.app:
            install_selected_apps(force_apps=[args.app])
        else:
            install_selected_apps()
    elif args.command == "config":
        if hasattr(args, 'app') and args.app:
            configure_selected_apps(force_apps=[args.app])
        else:
            configure_selected_apps()
    elif args.command == "app-switching":
        setup_app_switching()
    elif args.command == "bluetooth":
        if args.action == "list":
            subprocess.run(["python", "scripts/bluetooth_manager.py", "list"])
        elif args.action == "pair":
            subprocess.run(["python", "scripts/bluetooth_manager.py", "pair"])
        elif args.action == "connect" and args.gamepad:
            subprocess.run(["python", "scripts/bluetooth_manager.py", "connect", args.gamepad])
        elif args.action == "status" and args.gamepad:
            subprocess.run(["python", "scripts/bluetooth_manager.py", "status", args.gamepad])
        else:
            setup_bluetooth()
    elif args.command == "moonlight":
        setup_moonlight()
    elif args.command == "env-var":
        if hasattr(args, 'path') and args.path:
            from modules.system_configuration import setup_project_environment_variable
            setup_project_environment_variable(args.path)
        else:
            update_environment_variable_menu()
    elif args.command == "reboot":
        reboot_system()
    else:
        # Default to interactive mode
        main_menu_loop()


if __name__ == "__main__":
    main()
