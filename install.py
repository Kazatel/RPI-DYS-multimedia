import importlib
import config
import sys
import os
from utils.os_utils import get_raspberry_pi_model, get_codename
from modules.system_configuration import apply_locale_settings, apply_boot_config, create_or_overwrite_bash_aliases
from utils.os_utils import is_running_as_root
from modules.fstab_configurator import update_fstab_with_disks

if not is_running_as_root():
    print("❌ This script must be run with sudo.")
    print("👉 Please rerun with:\n")
    print("   sudo python install.py\n")
    sys.exit(1)



def ensure_supported_pi_environment(log):
    """
    Validates that the Raspberry Pi model and OS version are officially supported.
    If not supported and ON_OWN_RISK is disabled, exits the program.
    """
    # Check OS codename
    os_codename = get_codename()
    log.p_info(f"🔍 Detected OS codename: {os_codename}")

    # Check Raspberry Pi model
    pi_model = get_raspberry_pi_model()
    log.p_info(f"🔍 Detected Raspberry Pi model: {pi_model}")

    os_supported = os_codename in config.TESTED_OS_VERSION
    model_supported = pi_model in config.TESTED_MODELS

    if os_supported and model_supported:
        log.p_info("✅ OS version and Raspberry Pi model are officially supported.")
    else:
        log.p_warn("⚠️ One or more components are not officially supported:")
        if not os_supported:
            log.p_warn(f"   - OS '{os_codename}' is not in TESTED_OS_VERSION: {config.TESTED_OS_VERSION}")
        if not model_supported:
            log.p_warn(f"   - Pi model '{pi_model}' is not in TESTED_MODELS: {config.TESTED_MODELS}")

        if config.ON_OWN_RISK:
            log.p_warn("⚠️ Proceeding at your own risk (ON_OWN_RISK is enabled).")
        else:
            log.p_error("❌ Aborting installation — unsupported environment and ON_OWN_RISK is disabled.")
            sys.exit(1)

ensure_supported_pi_model()

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
    update_fstab_with_disks()

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
