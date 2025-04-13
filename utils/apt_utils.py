import subprocess
from utils.interaction import ask_user_choice

def get_available_versions(package_name):
    try:
        result = subprocess.check_output(
            ["apt-cache", "madison", package_name], text=True
        )
        versions = [line.split("|")[1].strip() for line in result.strip().split("\n")]
        return versions
    except subprocess.CalledProcessError:
        return []

def install_package(package_name, version=None):
    try:
        if version:
            subprocess.check_call(["sudo", "apt-get", "install", f"{package_name}={version}", "-y"])
        else:
            subprocess.check_call(["sudo", "apt-get", "install", package_name, "-y"])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package_installed(package_name):
    try:
        subprocess.check_call(["dpkg", "-s", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def handle_package_install(package_name, auto_select_version):
    available_versions = get_available_versions(package_name)

    if not available_versions:
        print(f"No versions found for {package_name}")
        return False

    if auto_select_version:
        selected_version = available_versions[0]
        print(f"[AUTO] Installing latest version of {package_name}: {selected_version}")
    else:
        selected_version = ask_user_choice(
            f"Select version of {package_name} to install", available_versions
        )

    success = install_package(package_name, selected_version)
    if not success:
        print(f"❌ Installation of {package_name} failed.")
        return False

    if not check_package_installed(package_name):
        print(f"❌ Post-installation check failed for {package_name}.")
        return False

    print(f"✅ {package_name} installed successfully.")
    return True

