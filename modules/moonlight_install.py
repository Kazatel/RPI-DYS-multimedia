import subprocess
import os
from utils.apt_utils import handle_package_install, check_package_installed
from utils.logger import Logger
from utils.interaction import ask_user_choice
import config

PACKAGE_NAME = "moonlight-qt"
REQUIRED_DEPS = ["git", "lsb-release"]

def is_moonlight_installed():
    return check_package_installed(PACKAGE_NAME)

def get_installed_version():
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Version}", PACKAGE_NAME],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def install_moonlight(log):
    log.info("\n➡️  Installing dependencies for Moonlight...")
    for dep in REQUIRED_DEPS:
        handle_package_install(dep, auto_update_packages=True, log=log)

    log.info("\n➡️  Setting up Moonlight repository...")
    try:
        log_file_path = log.get_log_file_path()
        with open(log_file_path, "a") as logfile:
            subprocess.run(
                [
                    "bash", "-c",
                    "curl -1sLf 'https://dl.cloudsmith.io/public/moonlight-game-streaming/moonlight-qt/setup.deb.sh' | "
                    "distro=raspbian codename=$(lsb_release -cs) sudo -E bash"
                ],
                check=True,
                stdout=logfile,
                stderr=subprocess.STDOUT
            )
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Failed to set up Moonlight repository: {e}")
        return False

    log.info("\n➡️  Installing Moonlight...")
    log.tail_note()
    return handle_package_install(PACKAGE_NAME, auto_update_packages=True, log=log)

def main_install(log=None):
    if log is None:
        log = Logger()

    if is_moonlight_installed():
        current_version = get_installed_version()
        if getattr(config, "AUTO_UPDATE_PACKAGES", False):
            log.info(f"🔁 Moonlight is already installed (version: {current_version}). Updating as AUTO_UPDATE_PACKAGES is enabled...")
        else:
            choice = ask_user_choice(
                f"✅ Moonlight is already installed (version: {current_version}). Do you want to update it?",
                {"y": "Yes, update", "n": "No, skip"}
            )
            if choice == "n":
                log.info("⏩ Skipping Moonlight update per user choice.")
                return

    if install_moonlight(log):
        log.info("\n✅ Moonlight installed successfully!")
    else:
        log.error("\n❌ Moonlight installation failed.")

def main_configure(log=None):
    # Moonlight doesn't require config by default — can leave this as a stub
    if log is None:
        log = Logger()
    log.info("ℹ️  No post-install configuration required for Moonlight.")

if __name__ == "__main__":
    main_install()
