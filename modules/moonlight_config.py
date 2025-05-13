"""
Moonlight Configuration Module

This module handles all configuration tasks for Moonlight, separate from installation.
"""

import os
import subprocess
import config
from utils.apt_utils import check_package_installed
from utils.logger import logger_instance as log
from utils.command_utils import run_command


def is_moonlight_installed():
    """
    Checks if Moonlight is already installed.

    Returns:
        bool: True if installed, False otherwise.
    """
    return check_package_installed("moonlight-qt")


def ensure_moonlight_directories():
    """
    Ensures that Moonlight directories exist with proper ownership
    """
    user = config.USER
    moonlight_dir = f"/home/{user}/.config/moonlight"
    
    # Check if the main Moonlight directory exists
    if not os.path.exists(moonlight_dir):
        log.info(f"📁 Creating Moonlight directory structure at {moonlight_dir}")
        # Create the main Moonlight directory
        os.makedirs(moonlight_dir, exist_ok=True)
        
        # Set proper ownership
        try:
            subprocess.run(["chown", f"{user}:{user}", moonlight_dir], check=True)
            log.info(f"✅ Created Moonlight directory with proper ownership")
        except Exception as e:
            log.error(f"❌ Failed to set ownership for {moonlight_dir}: {e}")
    else:
        # Check ownership of existing directory
        try:
            # Get the owner of the directory
            stat_info = os.stat(moonlight_dir)
            dir_uid = stat_info.st_uid
            dir_gid = stat_info.st_gid
            
            # Get the user's uid/gid
            import pwd
            user_info = pwd.getpwnam(user)
            user_uid = user_info.pw_uid
            user_gid = user_info.pw_gid
            
            # If ownership is wrong, fix it
            if dir_uid != user_uid or dir_gid != user_gid:
                log.warning(f"⚠️ Moonlight directory has incorrect ownership. Fixing...")
                subprocess.run(["chown", "-R", f"{user}:{user}", moonlight_dir], check=True)
                log.info(f"✅ Fixed Moonlight directory ownership")
        except Exception as e:
            log.error(f"❌ Failed to check/fix Moonlight directory ownership: {e}")


def configure_moonlight_settings():
    """
    Configure Moonlight settings based on config values
    """
    user = config.USER
    settings_file = f"/home/{user}/.config/moonlight/moonlight.conf"
    
    # Check if we have Moonlight settings in the config
    if not hasattr(config, "MOONLIGHT_SETTINGS") or not config.MOONLIGHT_SETTINGS:
        log.info("ℹ️ No Moonlight settings found in config. Using defaults.")
        return True
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    
    # Read existing settings if the file exists
    settings = {}
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line:
                        key, value = line.split("=", 1)
                        settings[key.strip()] = value.strip()
        except Exception as e:
            log.warning(f"⚠️ Failed to read existing Moonlight settings: {e}")
    
    # Update settings with values from config
    settings.update(config.MOONLIGHT_SETTINGS)
    
    # Write the updated settings
    try:
        with open(settings_file, "w") as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")
        
        # Set proper ownership
        subprocess.run(["chown", f"{user}:{user}", settings_file], check=True)
        
        log.info("✅ Updated Moonlight settings")
        return True
    except Exception as e:
        log.error(f"❌ Failed to update Moonlight settings: {e}")
        return False


def pair_with_host():
    """
    Pair Moonlight with a host PC running NVIDIA GameStream
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if we have host information in the config
    if not hasattr(config, "MOONLIGHT_HOST") or not config.MOONLIGHT_HOST:
        log.warning("⚠️ No Moonlight host information found in config.")
        return False
    
    host = config.MOONLIGHT_HOST
    
    log.info(f"🔄 Pairing with Moonlight host: {host}")
    log.info("⚠️ Please accept the pairing request on your host PC")
    
    try:
        # Run the pairing command
        result = run_command(
            ["moonlight", "pair", host],
            run_as_user=config.USER,
            log_live=True
        )
        
        if result.returncode == 0:
            log.info("✅ Successfully paired with Moonlight host")
            return True
        else:
            log.error(f"❌ Failed to pair with Moonlight host (exit code: {result.returncode})")
            return False
    except Exception as e:
        log.error(f"❌ Failed to pair with Moonlight host: {e}")
        return False


def verify_connection():
    """
    Verify the connection to the Moonlight host
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if we have host information in the config
    if not hasattr(config, "MOONLIGHT_HOST") or not config.MOONLIGHT_HOST:
        log.warning("⚠️ No Moonlight host information found in config.")
        return False
    
    host = config.MOONLIGHT_HOST
    
    log.info(f"🔍 Verifying connection to Moonlight host: {host}")
    
    try:
        # Run the list command to verify connection
        result = run_command(
            ["moonlight", "list", host],
            run_as_user=config.USER,
            log_live=True
        )
        
        if result.returncode == 0:
            log.info("✅ Successfully connected to Moonlight host")
            return True
        else:
            log.error(f"❌ Failed to connect to Moonlight host (exit code: {result.returncode})")
            return False
    except Exception as e:
        log.error(f"❌ Failed to connect to Moonlight host: {e}")
        return False


def create_desktop_shortcut():
    """
    Create a desktop shortcut for Moonlight
    
    Returns:
        bool: True if successful, False otherwise
    """
    user = config.USER
    desktop_dir = f"/home/{user}/Desktop"
    desktop_file = os.path.join(desktop_dir, "moonlight.desktop")
    
    # Create the desktop directory if it doesn't exist
    os.makedirs(desktop_dir, exist_ok=True)
    
    # Create the desktop file
    try:
        with open(desktop_file, "w") as f:
            f.write("""[Desktop Entry]
Name=Moonlight
Comment=NVIDIA GameStream client
Exec=moonlight-qt
Icon=${DYS_RPI}/media/moonlight.png
Terminal=false
Type=Application
Categories=Game;
""")
        
        # Set proper ownership and permissions
        subprocess.run(["chown", f"{user}:{user}", desktop_file], check=True)
        subprocess.run(["chmod", "755", desktop_file], check=True)
        
        log.info("✅ Created Moonlight desktop shortcut")
        return True
    except Exception as e:
        log.error(f"❌ Failed to create Moonlight desktop shortcut: {e}")
        return False


def main():
    """Main configuration function for Moonlight"""
    if not is_moonlight_installed():
        log.error("❌ Moonlight is not installed. Please install it first.")
        return False

    log.info("🎮 Configuring Moonlight...")
    
    # Ensure Moonlight directories exist with proper ownership
    ensure_moonlight_directories()
    
    # Configure Moonlight settings
    configure_moonlight_settings()
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    # Pair with host if specified in config
    if hasattr(config, "MOONLIGHT_PAIR") and config.MOONLIGHT_PAIR:
        pair_with_host()
    
    # Verify connection if specified in config
    if hasattr(config, "MOONLIGHT_VERIFY") and config.MOONLIGHT_VERIFY:
        verify_connection()
    
    log.info("✅ Moonlight configuration complete")
    return True


if __name__ == "__main__":
    main()
