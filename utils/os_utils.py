import os
import subprocess
import shutil
import pwd

def is_running_as_root():
    """Check if the script is run with sudo or as root."""
    return os.geteuid() == 0

def user_has_sudo_rights(user=None):
    """Check if a user has sudo privileges (without using sudo)."""
    try:
        if not user:
            user = os.getenv("SUDO_USER") or os.getenv("USER") or pwd.getpwuid(os.getuid()).pw_name
        groups = [g.gr_name for g in os.getgrouplist(user, pwd.getpwnam(user).pw_gid)]
        return 'sudo' in groups or 'wheel' in groups
    except Exception:
        return False

def is_command_available(command):
    return shutil.which(command) is not None

def get_codename():
    return subprocess.check_output(['lsb_release', '-cs'], text=True).strip().lower()

def is_supported(codenames=("bullseye", "bookworm")):
    return get_codename() in codenames
