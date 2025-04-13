import subprocess
import shutil

def is_command_available(command):
    return shutil.which(command) is not None

def get_codename():
    return subprocess.check_output(['lsb_release', '-cs'], text=True).strip().lower()

def is_supported(codenames=("bullseye", "bookworm")):
    return get_codename() in codenames
