import importlib
import sys
import os
import config
from utils.logger import Logger
from utils.os_utils import (
    get_raspberry_pi_model,
    get_codename,
    is_running_as_root
)
from modules.system_configuration import (
    apply_locale_settings,
    apply_boot_config,
    create_or_overwrite_bash_aliases
)
from modules.fstab_configurator import update_fstab_with_disks

log = Logger("installer.log")

# --- PRECHECK ---
if not is_running_as_root():
    print("❌ This script must be run with sudo.")
    print("👉 Please rerun with:\n")
    print("   sudo python install.py\n")
    sys.exit(1)


def ensure_supported_pi_environment():
    os_codename = get_codename()
    pi_model = get_raspberry_pi_model()

    log.p_info(f"🔍 Detected OS codename: {os_codename}")
    log.p_info(f"🔍 Detected Raspberry Pi model: {pi_model}")

    os_supported = os_codename in config.TESTED_OS_VERSION
    model_supported = pi_model in config.TESTED_MODELS

    if os_supported and model_supported:
        log.p_info("✅ OS version and Raspberry Pi model are officially supported.")
    else:
        log.p_warning("⚠️ One or more components are not officially supported:")
        if not os_supported:
            log.p_warninging(f"   - OS '{os_codename}' is not in TESTED_OS_VERSION: {config.TESTED_OS_VERSION}")
        if not model_supported:
            log.p_warning(f"   - Pi model '{pi_model}' is not in TESTED_MODELS: {config.TESTED_MODELS}")

        if config.ON_OWN_RISK:
            log.p_warning("⚠️ Proceeding at your own risk (ON_OWN_RISK is enabled).")
        else:
            log.p_error("❌ Aborting installation — unsupported environment and ON_OWN_RISK is disabled.")
            sys.exit(1)


# --- SYSTEM SETUP ---
def system_setup():
    ensure_supported_pi_environment()
    print("\n⚙️  Applying system configurations...")
    apply_boot_config()
    create_or_overwrite_bash_aliases()
    update_fstab_with_disks()
    # apply_locale_settings()  # Optional depending on setup
    print("\n🔁 System configuration complete. Please reboot before continuing.")


# --- APPLICATION INSTALLATION ---
MODULES_DIR = "modules"
INSTALLED_APPS = {
    "kodi": config.KODI,
    "retropie": config.RETROPIE,
    "moonlight": config.MOONLIGHT,
}

def install_selected_apps(force_apps=None):
    print("\n📦 Installing selected applications...")
    for app_name, should_install in INSTALLED_APPS.items():
        if force_apps or should_install:
            try:
                module_path = f"{MODULES_DIR}.{app_name}_install"
                module = importlib.import_module(module_path)
                if hasattr(module, "main"):
                    print(f"\n🚀 Starting installation for: {app_name.upper()}")
                    module.main()
                else:
                    print(f"⚠️  No main() function found in {module_path}.")
            except ModuleNotFoundError as e:
                print(f"❌ Module not found for {app_name}: {e}")


def post_install_configuration():
    print("\n🔧 Running post-install configuration...")
    try:
        from modules.retropie_post_config import configure_retropie
        configure_retropie()
    except ImportError:
        print("⚠️ Could not import post-install configuration module.")


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
    print("4) ⚙️  Advanced Mode")
    print("   - Run individual steps manually (no validation)")
    print("5) ❌ Exit")

def main_menu_loop():
    while True:
        print_main_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            system_setup()
        elif choice == "2":
            install_selected_apps()
        elif choice == "3":
            post_install_configuration()
        elif choice == "4":
            advanced_menu_loop()
        elif choice == "5":
            print("👋 Exiting installer.")
            sys.exit(0)
        else:
            print("❌ Invalid option. Please choose 1–5.")


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
        print("8) Run RetroPie post-config")
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
            post_install_configuration()
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")


if __name__ == "__main__":
    main_menu_loop()
