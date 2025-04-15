import os
import subprocess
import shutil
import pwd

def is_running_as_root():
    """Check if the script is run with sudo or as root."""
    return os.geteuid() == 0

def is_command_available(command):
    return shutil.which(command) is not None

def get_codename() -> str:
    """
    Returns the OS codename (e.g., 'bookworm', 'bullseye').
    """
    try:
        output = subprocess.check_output(['lsb_release', '-cs'], text=True).strip().lower()
        return output
    except subprocess.CalledProcessError:
        return "unknown"

def is_supported(current_codename: str, tested_versions: list) -> bool:
    """
    Checks if the current OS codename is in the list of tested versions.
    """
    return current_codename in [ver.lower() for ver in tested_versions]