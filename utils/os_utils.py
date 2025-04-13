import os
import subprocess
import shutil
import pwd

def is_running_as_root():
    """Check if the script is run with sudo or as root."""
    return os.geteuid() == 0

def is_command_available(command):
    return shutil.which(command) is not None

def get_codename():
    return subprocess.check_output(['lsb_release', '-cs'], text=True).strip().lower()

def is_supported(codenames=("bullseye", "bookworm")):
    return get_codename() in codenames
