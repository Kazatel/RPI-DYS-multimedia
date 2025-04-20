from utils.apt_utils import handle_package_install, check_package_installed
from utils.logger import logger_instance as log
from utils.interaction import ask_user_choice
from utils.os_utils import run_command
import config

PACKAGE_NAME = "moonlight-qt"
REQUIRED_DEPS = ["git", "lsb-release"]

def is_moonlight_installed(run_as_user="root"):
    """
    Checks if Moonlight is installed.
    """
    return check_package_installed(PACKAGE_NAME, run_as_user=run_as_user)

def get_installed_version(run_as_user="root"):
    """
    Retrieves the installed version of Moonlight.
    """
    try:
        result = run_command(
            ["dpkg-query", "-W", "-f=${Version}", PACKAGE_NAME],
            capture_output=True,
            run_as_user=run_as_user
        )
        return result.stdout.strip()
    except Exception:
        return None

def install_moonlight(log, run_as_user="root"):
    """
    Installs Moonlight and its dependencies.
    """
    log.info("\n➡️  Installing dependencies for Moonlight...")
    for dep in REQUIRED_DEPS:
        handle_package_install(dep, auto_update_packages=True,  run_as_user=run_as_user)

    log.info("\n➡️  Setting up Moonlight repository...")
    try:
        cmd = (
            "curl -1sLf 'https://dl.cloudsmith.io/public/moonlight-game-streaming/moonlight-qt/setup.deb.sh' | "
            "distro=raspbian codename=$(lsb_release -cs) sudo -E bash"
        )
        run_command(
            ["bash", "-c", cmd],
            run_as_user=run_as_user
        )
    except Exception as e:
        log.error(f"❌ Failed to set up Moonlight repository: {e}")
        return False

    log.info("\n➡️  Installing Moonlight...")
    log.tail_note()
    return handle_package_install(PACKAGE_NAME, auto_update_packages=True,  run_as_user=run_as_user)

def main_install():
    """
    Handles the installation of Moonlight.
    """
    run_as_user = getattr(config.APPLICATIONS.get("moonlight", {}), "user", "root")

    if is_moonlight_installed(run_as_user=run_as_user):
        current_version = get_installed_version(run_as_user=run_as_user)
        if getattr(config, "AUTO_UPDATE_PACKAGES", False):
            log.info(f"🔁 Moonlight is already installed (version: {current_version}). Updating as AUTO_UPDATE_PACKAGES is enabled...")
        else:
            choice = ask_user_choice(
                f"✅ Moonlight is already installed (version: {current_version}). Do you want to update it?",
                {"y": "Yes, update", "n": "No, skip"},
            )
            if choice == "n":
                log.info("⏩ Skipping Moonlight update per user choice.")
                return

    if install_moonlight(log, run_as_user=run_as_user):
        log.info("\n✅ Moonlight installed successfully!")
    else:
        log.error("\n❌ Moonlight installation failed.")

def main_configure():
    """
    Configures Moonlight after installation.
    """
    log.info("ℹ️  No post-install configuration required for Moonlight.")

if __name__ == "__main__":
    main_install()
