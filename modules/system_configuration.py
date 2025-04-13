﻿import os
import config
from datetime import datetime

def apply_locale_settings():
    locale = config.LOCALE_ALL.strip()

    print(f"🌐 Setting all system locale settings to {locale}...")

    try:
        subprocess.run(["sudo", "update-locale", f"LANGUAGE={locale}:en"], check=True)
        subprocess.run(["sudo", "update-locale", f"LC_ALL={locale}"], check=True)
        print("✅ Locale settings applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to apply locale settings: {e}")


def apply_boot_config():
    boot_config_path = "/boot/firmware/config.txt"
    marker_prefix = "# added by script"

    if not os.path.exists(boot_config_path):
        print(f"❌ Boot config not found at {boot_config_path}")
        return

    print("⚙️ Applying BOOT_* settings to /boot/firmware/config.txt")

    # Prepare marker line with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    marker_line = f"{marker_prefix} [{timestamp}]"

    # Read existing content
    try:
        with open(boot_config_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read {boot_config_path}: {e}")
        return

    # Remove existing marker block
    new_lines = []
    inside_old_block = False
    for line in lines:
        if line.startswith(marker_prefix):
            inside_old_block = True
            continue  # Skip marker line
        if inside_old_block:
            if line.strip() == "":
                inside_old_block = False
            continue
        new_lines.append(line.rstrip())

    # Add new block
    new_lines.append("")
    new_lines.append(marker_line)
    for key, value in config.__dict__.items():
        if key.startswith("BOOT_"):
            setting_name = key.replace("BOOT_", "")
            new_lines.append(f"{setting_name}={value}")

    # Write updated file
    try:
        with open(boot_config_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        print("✅ Boot configuration applied.")
    except Exception as e:
        print(f"❌ Failed to write to {boot_config_path}: {e}")

def create_or_overwrite_bash_aliases():
    """
    Creates or overwrites the ~/.bash_aliases file with the given content.

    Args:
        bash_aliases_content (str): The content to write to the file.
    """
    home_dir = os.path.expanduser("~")
    bash_aliases_path = os.path.join(home_dir, ".bash_aliases")
    bash_aliases_content = config.BASH_ALIASES
    print(f"⚙️ Writing aliases to {bash_aliases_path}")
    try:
        with open(bash_aliases_path, "w") as f:
            f.write(bash_aliases_content)
        print(f"✅ Successfully created or overwritten {bash_aliases_path}")
    except OSError as e:
        print(f"❌ Error creating or overwriting{bash_aliases_path}: {e}")


def main():
    apply_boot_config()
    create_or_overwrite_bash_aliases()


if __name__ == "__main__":
    main()

