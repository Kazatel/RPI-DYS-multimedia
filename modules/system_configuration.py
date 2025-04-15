import subprocess
import os
from utils.apt_utils import handle_package_install
from utils.logger import Logger
import config


def install_prerequisites(log):
    """
    Installs required prerequisite packages using apt.
    """
    log.p_info("🔧 Installing prerequisites using apt_utils...")
    for pkg in ["git", "lsb-release"]:
        handle_package_install(pkg, auto_select_version=True, log=log)


def clone_retropie(log):
    """
    Clones the RetroPie setup script if not already present.
    Logs the success or failure of the cloning process, and captures the git output to the log file.
    """
    log.p_info("📥 Cloning RetroPie setup script...")
    if not os.path.exists("RetroPie-Setup"):
        try:
            log_file_path = log.get_log_file_path()
            with open(log_file_path, "a") as logfile:
                subprocess.run([
                    "git", "clone", "--depth=1", "https://github.com/RetroPie/RetroPie-Setup.git"
                ], check=True, stdout=logfile, stderr=subprocess.STDOUT)
            log.p_info("✅ Successfully cloned RetroPie-Setup repository.")
        except subprocess.CalledProcessError:
            log.p_error("❌ Failed to clone RetroPie-Setup repository. See log for details.")
    else:
        log.p_info("✅ RetroPie-Setup folder already exists. Skipping clone.")



def run_setup_script(log):
    """
    Executes the RetroPie setup script and logs output to the logger's file.
    """
    log.p_info("🚀 Running RetroPie installation script...")
    os.chdir("RetroPie-Setup")

    subprocess.run(["chmod", "+x", "retropie_setup.sh", "retropie_packages.sh"])

    log_file_path = log.get_log_file_path()
    log.tail_note()

    try:
        with open(log_file_path, "a") as logfile:
            process = subprocess.Popen(
                ["sudo", "./retropie_packages.sh", "setup", "basic_install"],
                stdout=logfile,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            returncode = process.wait()
            if returncode != 0:
                log.p_error(f"❌ RetroPie installation failed. See log for details: {log_file_path}")
            else:
                log.p_info("✅ RetroPie installation completed successfully.")
    except Exception as e:
        log.p_error(f"❌ Error during RetroPie installation: {e}")


def is_retropie_installed():
    """
    Checks if RetroPie is already installed on the system.

    Returns:
        bool: True if installed, False otherwise.
    """
    return os.path.exists("/opt/retropie/configs")


def get_retropie_version():
    """
    Retrieves the installed RetroPie version.

    Returns:
        str or None: Version string, message, or None if not found.
    """
    if os.path.exists("/opt/retropie/VERSION"):
        try:
            result = subprocess.run(["cat", "/opt/retropie/VERSION"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Version file exists, but could not be read."
        except FileNotFoundError:
            return "Version file not found."
    else:
        return None


def main(log=None):
    """
    Main entry point for the RetroPie installation script.

    Args:
        log (Logger, optional): Optional Logger instance. If None, a new one is created.
    """
    if log is None:
        log = Logger()

    if is_retropie_installed():
        version = get_retropie_version()
        if version:
            log.p_info(f"✅ RetroPie is already installed. Version: {version}")
        else:
            log.p_info("✅ RetroPie is already installed.")
        return

    install_prerequisites(log)
    clone_retropie(log)
    run_setup_script(log)


if __name__ == "__main__":
    main()
