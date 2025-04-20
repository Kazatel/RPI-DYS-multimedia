from utils.interaction import ask_user_choice
from utils.os_utils import run_command
from utils.logger import get_logger as log


def get_available_versions(package_name, run_as_user="root"):
    """
    Retrieves available versions of a package from apt-cache.

    Args:
        package_name (str): The name of the package to query.
        log (Logger, optional): Logger instance for output.
        run_as_user (str): User context to run command under (default is root).

    Returns:
        list: A list of version strings (latest first). Empty if not found.
    """
    try:
        result = run_command(
            ["apt-cache", "madison", package_name],
            capture_output=True,
            run_as_user=run_as_user,
            log_path=log.get_log_file_path()
        )
        versions = [line.split("|")[1].strip() for line in result.stdout.strip().split("\n")]
        return versions
    except Exception:
        log.error(f"❌ Failed to fetch available versions for: {package_name}")
        return []


def install_package(package_name, version=None, run_as_user="root"):
    """
    Installs a package using apt-get, with optional versioning.

    Args:
        package_name (str): The package name to install.
        version (str, optional): Specific version to install.
        log (Logger, optional): Logger instance for output.
        run_as_user (str): User context to run command under.

    Returns:
        bool: True if installation succeeded, False otherwise.
    """
    command = (
        ["apt-get", "install", f"{package_name}={version}", "-y"]
        if version else
        ["apt-get", "install", package_name, "-y"]
    )


    log.info(f"🛠️ Installing package: {package_name}" + (f" (version {version})" if version else ""))
    log.debug(f"Running command: {' '.join(command)}")

    try:
        run_command(
            command,
            log_path=log.get_log_file_path(),
            run_as_user=run_as_user,
            capture_output=True
        )
        return True
    except Exception as e:
        log.error(f"❌ Installation of {package_name} failed.")
        log.debug(f"[APT ERROR] {e}")

        return False


def check_package_installed(package_name, run_as_user="root"):
    """
    Checks if a package is installed via dpkg.

    Args:
        package_name (str): The name of the package to check.
        run_as_user (str): User context to run command under.

    Returns:
        bool: True if installed, False otherwise.
    """
    try:
        run_command(
            ["dpkg", "-s", package_name],
            run_as_user=run_as_user
        )
        return True
    except Exception:
        return False


def handle_package_install(package_name, auto_update_packages=False, run_as_user="root"):
    """
    Orchestrates the full process of installing a package:
    - Fetches available versions
    - Prompts user if needed
    - Installs selected version
    - Verifies installation

    Args:
        package_name (str): Name of the package to install.
        auto_update_packages (bool): If True, selects latest version automatically.
        log (Logger, optional): Logger instance for output.
        run_as_user (str): User to run installation under.

    Returns:
        bool: True if package was installed and verified, False otherwise.
    """
    available_versions = get_available_versions(package_name, run_as_user=run_as_user)
    if not available_versions:
        return False

    if auto_update_packages:
        selected_version = available_versions[0]
        log.info(f"[AUTO] Installing latest version of {package_name}: {selected_version}")
    else:
        selected_version = ask_user_choice(
            f"Select version of {package_name} to install",
            available_versions,
            log=og.get_log_file_path()
        )

    success = install_package(package_name, selected_version, run_as_user=run_as_user)
    if not success:
        return False

    if not check_package_installed(package_name, run_as_user=run_as_user):
        log.error(f"❌ Post-installation check failed for {package_name}")
        return False

    log.info(f"✅ {package_name} installed successfully.")
    return True
