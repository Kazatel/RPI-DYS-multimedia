import os
import config
import subprocess
from datetime import datetime
from utils.logger import logger_instance as log


def apply_locale_settings():
    locale = config.LOCALE_ALL.strip()

    log.info(f"🌐 Setting all system locale settings to {locale}...")
    try:
        subprocess.run(["sudo", "update-locale", f"LANGUAGE={locale}:en"], check=True)
        subprocess.run(["sudo", "update-locale", f"LC_ALL={locale}"], check=True)
        log.info("✅ Locale settings applied successfully.")
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Failed to apply locale settings: {e}")


def apply_boot_config():
    boot_config_path = "/boot/firmware/config.txt"
    marker_prefix = "# added by script"

    if not os.path.exists(boot_config_path):
        log.error(f"❌ Boot config not found at {boot_config_path}")
        return

    log.info("⚙️ Applying BOOT_* settings to /boot/firmware/config.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    marker_line = f"{marker_prefix} [{timestamp}]"

    try:
        with open(boot_config_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        log.error(f"❌ Failed to read {boot_config_path}: {e}")
        return

    new_lines = []
    inside_old_block = False
    for line in lines:
        if line.startswith(marker_prefix):
            inside_old_block = True
            continue
        if inside_old_block:
            if line.strip() == "":
                inside_old_block = False
            continue
        new_lines.append(line.rstrip())

    new_lines.append("")
    new_lines.append(marker_line)
    for key, value in config.__dict__.items():
        if key.startswith("BOOT_"):
            setting_name = key.replace("BOOT_", "")
            new_lines.append(f"{setting_name}={value}")

    try:
        with open(boot_config_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        log.info("✅ Boot configuration applied.")
    except Exception as e:
        log.error(f"❌ Failed to write to {boot_config_path}: {e}")


def create_or_overwrite_bash_aliases():
    home_dir = os.path.join("/home", config.USER)
    bash_aliases_path = os.path.join(home_dir, ".bash_aliases")
    bash_aliases_content = config.BASH_ALIASES

    log.info(f"⚙️ Writing aliases to {bash_aliases_path}")
    try:
        with open(bash_aliases_path, "w") as f:
            f.write(bash_aliases_content)
        log.info(f"✅ Successfully created or overwritten {bash_aliases_path}")
    except OSError as e:
        log.error(f"❌ Error creating or overwriting {bash_aliases_path}: {e}")


def setup_project_environment_variable():
    """
    Set up a system-wide environment variable DYS_RPI pointing to the project directory
    This allows all scripts to reference the project directory directly
    """
    log.info("🔧 Setting up project environment variable DYS_RPI...")

    # Get the absolute path to the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    # Environment variable name
    env_var_name = "DYS_RPI"
    env_file_path = "/etc/environment"

    # Read current /etc/environment
    try:
        with open(env_file_path, "r") as f:
            current_content = f.read()
    except Exception as e:
        log.error(f"❌ Failed to read {env_file_path}: {e}")
        current_content = ""

    # Check if the variable is already set correctly
    env_line = f'{env_var_name}="{project_dir}"'
    if env_line in current_content:
        log.info(f"✅ Environment variable {env_var_name} already set to {project_dir}")
        return True

    # Remove any existing setting for this variable
    new_lines = []
    for line in current_content.splitlines():
        if not line.startswith(f"{env_var_name}="):
            new_lines.append(line)

    # Add the new environment variable
    new_lines.append(env_line)

    # Write back to /etc/environment
    try:
        with open(env_file_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        log.info(f"✅ Set {env_var_name} to {project_dir}")
        log.info("⚠️ A system reboot is required for the environment variable to take effect")
        return True
    except Exception as e:
        log.error(f"❌ Failed to set environment variable: {e}")
        return False


def main():
    apply_boot_config()
    create_or_overwrite_bash_aliases()
    setup_project_environment_variable()
    apply_locale_settings()


if __name__ == "__main__":
    main()
