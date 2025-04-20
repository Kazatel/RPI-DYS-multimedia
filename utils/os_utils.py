import os
import sys
import subprocess
import shutil
import pwd
import time


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

def get_raspberry_pi_model():
    try:
        with open("/proc/device-tree/model", "r") as f:
            return f.read().strip("\x00\n ")
    except FileNotFoundError:
        try:
            result = subprocess.run(["cat", "/sys/firmware/devicetree/base/model"], capture_output=True, text=True)
            return result.stdout.strip("\x00\n ")
        except Exception:
            return "Unknown"


def reboot_countdown(seconds=10):
    print("\n🔁 System will reboot in {} seconds...".format(seconds))
    print("⏳ Press Ctrl+C to cancel.\n")
    print("\n📌 After reboot, re-run the script and choose the next step to continue.\n")

    try:
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r💤 Rebooting in {i:2d} seconds... ")
            sys.stdout.flush()
            time.sleep(1)
        print("\n\n🚀 Rebooting now...")
        time.sleep(1)
        os.system("sudo reboot")
    except KeyboardInterrupt:
        print("\n❌ Reboot cancelled. You're still in control. ✋")


def get_home_directory():
    """
    Returns the home directory of the user running the script, even when executed with sudo.
    """
    if "SUDO_USER" in os.environ:
        return os.path.expanduser(f"~{os.environ['SUDO_USER']}")
    return os.path.expanduser("~")

def get_username():
    """
    Returns the name of the non-root user, even when running with sudo.
    """
    return os.environ.get("SUDO_USER") or os.environ.get("USER") or pwd.getpwuid(os.getuid()).pw_name


import subprocess
import os

def run_command(command, log_path=None, run_as_user=None, cwd=None, log_live=False, use_bash_wrapper=True):

    """
    Run a shell command with optional logging, user context, and live logging.

    Args:
        command (list or str): Command to run.
        log_path (str, optional): Path to log file.
        run_as_user (str, optional): Username to run the command as (requires sudo).
        cwd (str, optional): Directory to run the command from.
        log_live (bool): If True, stream output line-by-line to log as command runs.

    Returns:
        subprocess.CompletedProcess or int: CompletedProcess if log_live=False, return code if log_live=True
    """
    if isinstance(command, str) and use_bash_wrapper:
        command = ["bash", "-c", command]

    if run_as_user and run_as_user != "root":
        command = ["sudo", "-u", run_as_user] + command

    logfile = open(log_path, "a") if log_path else None

    try:
        if log_live:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            for line in process.stdout:
                if logfile:
                    logfile.write(line)
                    logfile.flush()
                else:
                    print(line, end="")

            return_code = process.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)
            return return_code

        else:
            result = subprocess.run(
                command,
                check=True,
                stdout=logfile if logfile else subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                text=True,
            )
            return result

    finally:
        if logfile:
            logfile.close()
