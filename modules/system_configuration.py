import config
import os

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
    if not os.path.exists(boot_config_path):
        print(f"❌ Boot config not found at {boot_config_path}")
        return

    print("⚙️ Applying BOOT_* settings to /boot/firmware/config.txt")
    lines_to_append = ["\n# added by script"]

    for key, value in config.__dict__.items():
        if key.startswith("BOOT_"):
            setting_name = key.replace("BOOT_", "")
            lines_to_append.append(f"{setting_name}={value}")

    try:
        with open(boot_config_path, "a") as f:
            f.write("\n".join(lines_to_append) + "\n")
        print("✅ Boot configuration applied.")
    except Exception as e:
        print(f"❌ Failed to write to {boot_config_path}: {e}")


def main():
    apply_boot_config()


if __name__ == "__main__":
    main()

