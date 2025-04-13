import importlib
import config
import sys
import os

from modules.system_configuration import apply_locale_settings, apply_overclock_settings

MODULES_DIR = "modules"

INSTALLED_APPS = {
    "kodi": config.KODI,
    "retropie": config.RETROPIE,
    "moonlight": config.MOONLIGHT,
}

def process_system_configurations():
    print("\n⚙️  Applying system configurations...")
    apply_locale_settings()
    apply_overclock_settings()

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
