import subprocess
from utils.interaction import ask_user_choice

def get_available_versions(package_name, log=None):
    """
    Retrieves available versions of a package from apt-cache.

    Args:
        package_name (str): The name of the package to query.
        log (Logger, optional): Logger instance for output.

    Returns:
        list: A list of version strings (latest first). Empty if not found.
    """
    try:
        result = subprocess.check_output(
            ["apt-cache", "madison", package_name], text=True
        )
        versions = [line.split("|")[1].strip() for line in result.strip().split("\n")]
        return versions
    except subprocess.CalledProcessError:
        if log:
            log.error(f"Failed to fetch available versions for: {package_name}")
        else:
            print(f"❌ Failed to fetch available versions for: {package_name}")
        return []


def install_package(package_name, version=None, log=None):
    """
    Installs a package using apt-get, with optional versioning.
    Captures stdout/stderr and logs output if log is provided.

    Args:
        package_name (str): The package name to install.
        version (str, optional): Specific version to install.
        log (Logger, optional): Logger instance for output.

    Returns:
        bool: True if installation succeeded, False otherwise.
    """
    command = (
        ["sudo", "apt-get", "install", f"{package_name}={version}", "-y"]
        if version else
        ["sudo", "apt-get", "install", package_name, "-y"]
    )

    if log:
        log.info(f"🛠️ Installing package: {package_name}" + (f" (version {version})" if version else ""))
        log.debug(f"Running command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        if log:
            log.debug(f"[APT OUTPUT] {result.stdout.strip()}")
        return True

    except subprocess.CalledProcessError as e:
        if log:
            log.error(f"❌ Installation of {package_name} failed. See log for details.")
            log.debug(f"[APT ERROR] {e.stderr.strip()}")
        else:
            print(f"❌ Installation failed: {package_name}")
        return False


def check_package_installed(package_name):
    """
    Checks if a package is installed via dpkg.

    Args:
        package_name (str): The name of the package to check.

    Returns:
        bool: True if installed, False otherwise.
    """
    try:
        subprocess.check_call(
            ["dpkg", "-s", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def handle_package_install(package_name, auto_select_version=False, log=None):
    """
    Orchestrates the full process of installing a package:
    - Fetches available versions
    - Prompts user if needed
    - Installs selected version
    - Verifies installation

    Args:
        package_name (str): Name of the package to install.
        auto_select_version (bool): If True, selects latest version automatically.
        log (Logger, optional): Logger instance for output.

    Returns:
        bool: True if package was installed and verified, False otherwise.
    """
    available_versions = get_available_versions(package_name, log=log)

    if not available_versions:
        return False

    if auto_select_version:
        selected_version = available_versions[0]
        if log:
            log.info(f"[AUTO] Installing latest version of {package_name}: {selected_version}")
        else:
            print(f"[AUTO] Installing latest version of {package_name}: {selected_version}")
    else:
        selected_version = ask_user_choice(
            f"Select version of {package_name} to install",
            available_versions,
            log=log
        )

    success = install_package(package_name, selected_version, log=log)
    if not success:
        return False

    if not check_package_installed(package_name):
        if log:
            log.error(f"Post-installation check failed for {package_name}")
        else:
            print(f"❌ Post-installation check failed for {package_name}")
        return False

    if log:
        log.info(f"✅ {package_name} installed successfully.")
    else:
        print(f"✅ {package_name} installed successfully.")
    return True
