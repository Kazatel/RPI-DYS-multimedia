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
    subprocess.run(["sudo", "./retropie_packages.sh", "nonint", "install_all"])


def main():
    install_prerequisites()
    clone_retropie()
    run_setup_script()


if __name__ == "__main__":
    main()

