import importlib
import config
import sys
import os

from modules.system_configuration import apply_locale_settings, apply_boot_config, create_or_overwrite_bash_aliases
from utils.os_utils import is_running_as_root

if not is_running_as_root():
    print("❌ This script must be run with sudo.")
    print("👉 Please rerun with:\n")
    print("   sudo python install.py\n")
    sys.exit(1)


MODULES_DIR = "modules"

INSTALLED_APPS = {
    "kodi": config.KODI,
    "retropie": config.RETROPIE,
    "moonlight": config.MOONLIGHT,
}

def process_system_configurations():
    print("\n⚙️  Applying system configurations...")
    #apply_locale_settings()
    apply_boot_config()
    create_or_overwrite_bash_aliases()

def install_selected_apps():
    print("\n📦 Installing selected applications...")
    for app_name, should_install in INSTALLED_APPS.items():
        if should_install:
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

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ["system", "all"]:
        process_system_configurations()

    if mode in ["apps", "all"]:
        install_selected_apps()
