import subprocess
import os
from utils.apt_utils import handle_package_install
import config

def install_prerequisites():
    print("🔧 Installing prerequisites using apt_utils...")
    for pkg in ["git", "lsb-release"]:
        handle_package_install(pkg, auto_select_version=True)

def clone_retropie():
    print("📥 Cloning RetroPie setup script...")
    if not os.path.exists("RetroPie-Setup"):
        subprocess.run([
            "git", "clone", "--depth=1", "https://github.com/RetroPie/RetroPie-Setup.git"
        ])
    else:
        print("✅ RetroPie-Setup folder already exists. Skipping clone.")

def run_setup_script():
    print("🚀 Running RetroPie installation script...")
    os.chdir("RetroPie-Setup")
    subprocess.run(["chmod", "+x", "retropie_setup.sh"])
    subprocess.run(["chmod", "+x", "retropie_packages.sh"])
    subprocess.run(["sudo", "./retropie_packages.sh", "setup", "basic_install"])

def is_retropie_installed():
    """Checks if RetroPie is installed."""
    return os.path.exists("/opt/retropie/configs")

def get_retropie_version():
    """Gets the RetroPie version, if installed."""
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

def main():
    if is_retropie_installed():
        version = get_retropie_version()
        if version:
            print(f"✅ RetroPie is already installed. Version: {version}")
        else:
            print("✅ RetroPie is already installed.")
        return  # Exit the script

    install_prerequisites()
    clone_retropie()
    run_setup_script()

if __name__ == "__main__":
    main()