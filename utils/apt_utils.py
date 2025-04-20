from utils.interaction import ask_user_choice
from utils.os_utils import run_command


def get_available_versions(package_name, log=None, run_as_user="root"):
    """
    Retrieves available versions of a package from apt-cache.

    Args:
        package_name (str): The name of the package to query.
        log (Logger, optional): Logger instance for output.
        run_as_user (str): User context to run command under (default is root).

    Returns:
        list: A list of version strings (latest first). Empty if not found.
    """
    print(log)
    print(dir(log))
    log_path = log.get_log_file_path() 
    print (log_path)
    result = run_command(
        ["apt-cache", "madison", package_name],
        capture_output=True,
        run_as_user=run_as_user,
        log_path=log_path
    )

    if log:
        log.debug(f"[MADISON RAW OUTPUT] {repr(result.stdout)}")

    output = result.stdout.strip()
    lines = output.split("\n")

    versions = []
    for line in lines:
        parts = line.split("|")
        if len(parts) > 1:
            versions.append(parts[1].strip())
        else:
            if log:
                log.warning(f"Skipping unrecognized madison line: {line}")

    return versions






def install_package(package_name, version=None, log=None, run_as_user="root"):
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

    if log:
        log.info(f"🛠️ Installing package: {package_name}" + (f" (version {version})" if version else ""))
        log.debug(f"Running command: {' '.join(command)}")

    try:
        run_command(
            command,
            log_path=log.get_log_file_path() if log else None,
            run_as_user=run_as_user,
            capture_output=True
        )
        return True
    except Exception as e:
        if log:
            log.error(f"❌ Installation of {package_name} failed.")
            log.debug(f"[APT ERROR] {e}")
        else:
            print(f"❌ Installation failed: {package_name}")
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


def handle_package_install(package_name, auto_update_packages=False, log=None, run_as_user="root"):
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
    available_versions = get_available_versions(package_name, log=log, run_as_user=run_as_user)
    if not available_versions:
        return False

    if auto_update_packages:
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

    success = install_package(package_name, selected_version, log=log, run_as_user=run_as_user)
    if not success:
        return False

    if not check_package_installed(package_name, run_as_user=run_as_user):
        if log:
            log.error(f"❌ Post-installation check failed for {package_name}")
        else:
            print(f"❌ Post-installation check failed for {package_name}")
        return False

    if log:
        log.info(f"✅ {package_name} installed successfully.")
    else:
        print(f"✅ {package_name} installed successfully.")
    return True
