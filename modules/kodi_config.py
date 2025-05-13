"""
Kodi Configuration Module

This module handles all configuration tasks for Kodi, separate from installation.
"""

import os
import subprocess
import pwd
import config
from utils.xml_utils import insert_xml_if_missing
from utils.apt_utils import check_package_installed
from utils.logger import logger_instance as log
from utils.command_utils import run_command


def is_kodi_installed():
    """
    Checks if Kodi is already installed.

    Returns:
        bool: True if installed, False otherwise.
    """
    return check_package_installed("kodi")


def generate_kodi_source_block(name, url, pathversion="1", allowsharing=True):
    """
    Generates a Kodi XML <source> block.

    Args:
        name (str): Name of the source.
        url (str): URL or path of the source.
        pathversion (str, optional): Path version. Defaults to "1".
        allowsharing (bool, optional): Whether to allow sharing. Defaults to True.

    Returns:
        str: XML string block for the Kodi source.
    """
    allowsharing_str = "<allowsharing>true</allowsharing>" if allowsharing else ""
    return f'''
    <source>
        <n>{name}</n>
        <path pathversion="{pathversion}">{url}</path>
        {allowsharing_str}
    </source>
    '''


def configure_kodi_sources():
    """
    Ensures the Kodi sources.xml file exists with a base structure,
    then inserts configured repositories if they are missing.
    """
    xml_file = os.path.expanduser(config.KODI_REPOSITORY_FILE_PATH)
    target_section = "sources-files"

    if not os.path.exists(xml_file):
        os.makedirs(os.path.dirname(xml_file), exist_ok=True)
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write("""<sources>
    <programs>
        <default pathversion="1"></default>
    </programs>
    <video>
        <default pathversion="1"></default>
    </video>
    <music>
        <default pathversion="1"></default>
    </music>
    <pictures>
        <default pathversion="1"></default>
    </pictures>
    <files>
        <default pathversion="1"></default>
    </files>
    <games>
        <default pathversion="1"></default>
    </games>
</sources>""")

    for repo in config.KODI_REPOSITORIES:
        name = repo.get("name")
        url = repo.get("url")
        pathversion = repo.get("pathversion", "1")
        allowsharing = repo.get("allowsharing", True)

        xml_block = generate_kodi_source_block(name, url, pathversion, allowsharing)
        insert_xml_if_missing(xml_file, target_section, xml_block)


def ensure_kodi_directories():
    """
    Ensures that Kodi directories exist with proper ownership
    """
    user = config.USER
    kodi_dir = f"/home/{user}/.kodi"

    # Check if the main Kodi directory exists
    if not os.path.exists(kodi_dir):
        log.info(f"📁 Creating Kodi directory structure at {kodi_dir}")
        # Create the main Kodi directory and essential subdirectories
        for subdir in ["", "addons", "userdata", "media", "system", "temp"]:
            dir_path = os.path.join(kodi_dir, subdir)
            os.makedirs(dir_path, exist_ok=True)
            # Set proper ownership immediately
            try:
                subprocess.run(["chown", f"{user}:{user}", dir_path], check=True)
            except Exception as e:
                log.error(f"❌ Failed to set ownership for {dir_path}: {e}")
        log.info(f"✅ Created Kodi directory structure with proper ownership")
    else:
        # Check ownership of existing directories
        try:
            # Get the owner of the .kodi directory
            stat_info = os.stat(kodi_dir)
            dir_uid = stat_info.st_uid
            dir_gid = stat_info.st_gid

            # Get the user's uid/gid
            user_info = pwd.getpwnam(user)
            user_uid = user_info.pw_uid
            user_gid = user_info.pw_gid

            # If ownership is wrong, fix it
            if dir_uid != user_uid or dir_gid != user_gid:
                log.warning(f"⚠️ Kodi directory has incorrect ownership. Fixing...")
                subprocess.run(["chown", "-R", f"{user}:{user}", kodi_dir], check=True)
                log.info(f"✅ Fixed Kodi directory ownership")
        except Exception as e:
            log.error(f"❌ Failed to check/fix Kodi directory ownership: {e}")


def launch_and_kill_kodi():
    """
    Launch Kodi briefly to initialize configuration folders, then kill it
    """
    try:
        # Ensure Kodi directories exist with proper ownership
        ensure_kodi_directories()

        command = "(kodi & sleep 10 && killall kodi.bin)"
        return_code = run_command(
            command,
            run_as_user=config.USER,
            log_live=True,
            use_bash_wrapper=True
        )
        log.info(f"✅ Kodi launched and killed successfully (exit code: {return_code})")
        return True
    except Exception as e:
        log.error("❌ Failed to launch and kill Kodi.")
        log.debug(f"Error: {e}")
        return False


def enable_unknown_sources():
    """
    Enable unknown sources in Kodi to allow installation of third-party addons
    """
    user = config.USER
    settings_file = f"/home/{user}/.kodi/userdata/advancedsettings.xml"
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    
    # Check if the file exists
    if not os.path.exists(settings_file):
        # Create a new file with unknown sources enabled
        with open(settings_file, "w") as f:
            f.write("""<advancedsettings>
    <general>
        <addonupdates>1</addonupdates>
    </general>
</advancedsettings>""")
        log.info("✅ Created advancedsettings.xml with unknown sources enabled")
    else:
        # Check if the file already has the setting
        with open(settings_file, "r") as f:
            content = f.read()
        
        if "<addonupdates>1</addonupdates>" in content:
            log.info("✅ Unknown sources already enabled in advancedsettings.xml")
        else:
            # Add the setting to the existing file
            xml_block = """    <general>
        <addonupdates>1</addonupdates>
    </general>"""
            insert_xml_if_missing(settings_file, "advancedsettings", xml_block)
            log.info("✅ Enabled unknown sources in advancedsettings.xml")
    
    # Set proper ownership
    try:
        subprocess.run(["chown", f"{user}:{user}", settings_file], check=True)
    except Exception as e:
        log.error(f"❌ Failed to set ownership for {settings_file}: {e}")
    
    return True


def install_addon(addon_id, addon_zip_path):
    """
    Install a Kodi addon from a zip file
    
    Args:
        addon_id (str): The addon ID
        addon_zip_path (str): Path to the addon zip file
        
    Returns:
        bool: True if successful, False otherwise
    """
    user = config.USER
    addons_dir = f"/home/{user}/.kodi/addons"
    
    # Create the addons directory if it doesn't exist
    os.makedirs(addons_dir, exist_ok=True)
    
    # Set proper ownership
    try:
        subprocess.run(["chown", f"{user}:{user}", addons_dir], check=True)
    except Exception as e:
        log.error(f"❌ Failed to set ownership for {addons_dir}: {e}")
    
    # TODO: Implement addon installation from zip
    # This would require extracting the zip file to the addons directory
    
    return True


def main():
    """Main configuration function for Kodi"""
    if not is_kodi_installed():
        log.error("❌ Kodi is not installed. Please install it first.")
        return False

    log.info("📺 Configuring Kodi...")
    
    # Ensure Kodi directories exist with proper ownership
    ensure_kodi_directories()
    
    # Launch Kodi briefly to initialize configuration folders
    launch_and_kill_kodi()
    
    # Configure Kodi sources
    configure_kodi_sources()
    
    # Enable unknown sources
    enable_unknown_sources()
    
    # Final check to ensure all directories have proper ownership
    ensure_kodi_directories()
    
    log.info("✅ Kodi configuration complete")
    return True


if __name__ == "__main__":
    main()
