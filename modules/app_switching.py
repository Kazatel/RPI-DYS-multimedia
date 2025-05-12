"""
App Switching Integration Module
Handles setup of app switching between GUI applications
"""

import os
import subprocess
import shutil
import tempfile
import config
from utils.logger import logger_instance as log
from utils.error_handler import handle_error
from modules.es_config_updater import ensure_es_systems_config

def get_app_switch_path():
    """Get the path to the app_switch.py script using the DYS_RPI environment variable"""
    dys_rpi = os.environ.get('DYS_RPI')
    if dys_rpi:
        return os.path.join(dys_rpi, "scripts", "app_switch.py")
    else:
        # Fallback to the old path if DYS_RPI is not set
        return os.path.expanduser("~/bin/app_switch.py")

def update_paths():
    """
    No need to update paths since we're using $HOME and os.path.expanduser
    which automatically resolve to the correct home directory
    """
    with log.log_section("Checking paths in components"):
        log.info("✅ Using $HOME and expanduser for paths - no updates needed")
        return True

@handle_error(exit_on_error=False)
def install_kodi_addon():
    """
    Install the Kodi app switcher addon

    Returns:
        bool: True if successful, False otherwise
    """
    with log.log_section("Installing Kodi Addon"):
        # Check if Kodi is enabled
        if not config.APPLICATIONS.get("kodi", {}).get("enabled", False):
            log.info("Kodi is not enabled, skipping addon installation")
            return True

        user = config.USER

        # Get the addon source directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        addon_source_dir = os.path.join(project_dir, "addons", "script.switcher")

        if not os.path.exists(addon_source_dir):
            log.error(f"Kodi addon source directory not found at {addon_source_dir}")
            return False

        # Determine Kodi directories
        kodi_dir = f"/home/{user}/.kodi"
        kodi_addon_dir = f"{kodi_dir}/addons/script.switcher"
        kodi_userdata_dir = f"{kodi_dir}/userdata"

        # Check if the main Kodi directory exists
        if not os.path.exists(kodi_dir):
            log.warning(f"⚠️ Kodi directory not found at {kodi_dir}. Creating it with proper ownership.")
            # Create the main Kodi directory and essential subdirectories
            for subdir in ["", "addons", "userdata", "media", "system", "temp"]:
                dir_path = os.path.join(kodi_dir, subdir)
                os.makedirs(dir_path, exist_ok=True)
                # Set proper ownership immediately
                subprocess.run(["chown", f"{user}:{user}", dir_path], check=True)
            log.info(f"✅ Created Kodi directory structure with proper ownership")
        else:
            # Just ensure the addon directory exists
            os.makedirs(os.path.dirname(kodi_addon_dir), exist_ok=True)
            # Make sure it has proper ownership
            subprocess.run(["chown", f"{user}:{user}", os.path.dirname(kodi_addon_dir)], check=True)

        # Remove existing addon directory if it exists
        if os.path.exists(kodi_addon_dir):
            log.info(f"Removing existing Kodi addon at {kodi_addon_dir}")
            try:
                shutil.rmtree(kodi_addon_dir)
            except Exception as e:
                log.error(f"Failed to remove existing Kodi addon: {e}")
                return False

        # Copy the addon to Kodi's addon directory
        try:
            log.info(f"Copying Kodi addon to {kodi_addon_dir}")
            shutil.copytree(addon_source_dir, kodi_addon_dir)

            # Set proper ownership
            subprocess.run(["chown", "-R", f"{user}:{user}", kodi_addon_dir], check=True)
            log.info("✅ Kodi addon installed successfully")

            # Enable the addon in Kodi's addon database
            # First create the addon_data directory
            addon_data_dir = f"{kodi_userdata_dir}/addon_data/script.switcher"
            os.makedirs(addon_data_dir, exist_ok=True)
            subprocess.run(["chown", "-R", f"{user}:{user}", addon_data_dir], check=True)

            # Create settings.xml
            settings_path = os.path.join(addon_data_dir, "settings.xml")
            with open(settings_path, "w") as f:
                f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n</settings>')
            subprocess.run(["chown", f"{user}:{user}", settings_path], check=True)

            # Run the enable_addon.py script to update Kodi's database
            enable_script = os.path.join(kodi_addon_dir, "enable_addon_improved.py")
            try:
                log.info("Running improved script to enable addon in Kodi")
                subprocess.run(["python3", enable_script], check=True)
                log.info("✅ Addon should be enabled now")
            except Exception as e:
                log.warning(f"Failed to run enable script: {e}")
                log.info("⚠️ The addon will need to be enabled manually in Kodi")
                log.info("1. In Kodi, go to Settings > Add-ons")
                log.info("2. Select 'My Add-ons' > 'Program add-ons'")
                log.info("3. Find 'App Switcher' and enable it")

            return True
        except Exception as e:
            log.error(f"Failed to install Kodi addon: {e}")
            return False


def setup_app_switching(autostart=None):
    """
    Set up app switching between GUI applications

    Args:
        autostart: Which application to start on boot (default: from config)

    Returns:
        bool: True if successful, False otherwise
    """
    with log.log_section("App Switching Setup"):
        log.info("🔄 Setting up app switching between GUI applications")

        # Get all enabled GUI apps
        gui_apps = get_gui_apps()

        if not gui_apps:
            log.error("No enabled GUI apps found in configuration")
            return False

        log.info(f"Found {len(gui_apps)} enabled GUI apps: {', '.join(gui_apps.keys())}")

        # Determine boot app
        if not autostart:
            autostart = getattr(config, "DEFAULT_BOOT_APP", None)

        if not autostart or autostart not in gui_apps:
            log.warning(f"Invalid or missing boot app: {autostart}")
            autostart = next(iter(gui_apps.keys()))
            log.info(f"Using first available GUI app: {autostart}")

        # Install services
        if not install_services():
            return False

        # Create desktop shortcuts
        if not create_desktop_shortcuts(gui_apps):
            return False

        # Integrate with RetroPie if it's enabled
        if "retropie" in gui_apps:
            integrate_with_retropie(gui_apps)

        # Install Kodi addon if Kodi is enabled
        if "kodi" in gui_apps:
            install_kodi_addon()

        # Update paths in Kodi addon, desktop shortcuts, and RetroPie ports scripts
        update_paths()

        # Configure autostart
        if not configure_autostart(gui_apps, autostart):
            return False

        log.info("✅ App switching setup completed successfully")
        return True

def get_gui_apps():
    """Get all enabled GUI apps from the configuration"""
    gui_apps = {}
    for app_name, app_config in config.APPLICATIONS.items():
        if app_config.get("enabled", False) and app_config.get("type") == "GUI":
            gui_apps[app_name] = app_config
    return gui_apps

def install_services():
    """
    Set up app switching scripts using the DYS_RPI environment variable
    No need to copy scripts to ~/bin anymore
    """
    with log.log_section("Setting up app switching scripts"):
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        scripts_dir = os.path.join(project_dir, "scripts")

        # List of scripts to check
        script_files = [
            "app_switch.py",
            "service_manager.sh"
        ]

        # Check if all scripts exist
        for script_file in script_files:
            script_path = os.path.join(scripts_dir, script_file)
            if not os.path.exists(script_path):
                log.error(f"Script not found at {script_path}")
                return False

            # Make sure the script is executable
            os.chmod(script_path, 0o755)
            log.info(f"✅ Made {script_file} executable")

        # Remove any old versions of the script from system locations and ~/bin
        try:
            user = config.USER
            old_locations = [
                "/usr/local/bin/app_switch.sh",
                "/usr/bin/app_switch.sh",
                "/opt/retropie/app_switch.sh",
                f"/home/{user}/bin/app_switch.sh",
                f"/home/{user}/bin/app_switch.py",
                f"/home/{user}/bin/service_manager.sh",
                f"/home/{user}/bin/service_manager.py"
            ]

            for old_location in old_locations:
                if os.path.exists(old_location):
                    try:
                        log.info(f"Removing old script from {old_location}")
                        if old_location.startswith(f"/home/{user}"):
                            # User's files can be removed directly
                            os.remove(old_location)
                        else:
                            # System files need sudo
                            subprocess.run(["sudo", "rm", old_location], check=True)
                    except Exception as e:
                        log.warning(f"⚠️ Failed to remove old script at {old_location}: {e}")

            log.info("✅ App switching scripts setup completed")
            log.info("✅ Scripts will be accessed using the DYS_RPI environment variable")
            return True
        except Exception as e:
            log.error(f"❌ Failed to set up app switching scripts: {e}")
            return False

def create_desktop_shortcuts(gui_apps):
    """Create desktop shortcuts for easy switching with custom icons"""
    with log.log_section("Creating desktop shortcuts"):
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Create icons directory if it doesn't exist
        user = config.USER
        icons_dir = f"/home/{user}/Pictures/icons"
        os.makedirs(icons_dir, exist_ok=True)

        # Set proper ownership for the icons directory
        try:
            subprocess.run(["chown", f"{user}:{user}", icons_dir], check=True)
            log.info(f"✅ Created icons directory at {icons_dir}")
        except Exception as e:
            log.warning(f"⚠️ Failed to set ownership for icons directory: {e}")

        # Copy icons from project media directory to user's icons directory
        project_dir = os.path.dirname(script_dir)
        media_dir = os.path.join(project_dir, "media")

        if os.path.exists(media_dir):
            for app_name in gui_apps.keys():
                icon_file = f"{app_name}.png"
                source_icon = os.path.join(media_dir, icon_file)
                dest_icon = os.path.join(icons_dir, icon_file)

                if os.path.exists(source_icon):
                    try:
                        shutil.copy2(source_icon, dest_icon)
                        subprocess.run(["chown", f"{user}:{user}", dest_icon], check=True)
                        log.info(f"✅ Copied icon for {app_name} to {icons_dir}")
                    except Exception as e:
                        log.warning(f"⚠️ Failed to copy icon for {app_name}: {e}")
        else:
            log.warning(f"⚠️ Media directory not found at {media_dir}")

        # Create desktop files in system, user, and root locations
        applications_dir = "/usr/share/applications"  # System-wide applications
        user_desktop_dir = f"/home/{user}/Desktop"    # User's desktop
        root_desktop_dir = "/root/Desktop"            # Root user's desktop

        # Create user's desktop directory if it doesn't exist
        os.makedirs(user_desktop_dir, exist_ok=True)
        subprocess.run(["chown", f"{user}:{user}", user_desktop_dir], check=True)

        # Create root's desktop directory if it doesn't exist
        try:
            subprocess.run(["sudo", "mkdir", "-p", root_desktop_dir], check=True)
            log.info(f"✅ Created or verified root desktop directory at {root_desktop_dir}")
        except Exception as e:
            log.warning(f"⚠️ Failed to create root desktop directory: {e}")

        for app_name, app_config in gui_apps.items():
            display_name = app_config.get("display_name", app_name.capitalize())
            desktop_file = f"{app_name}.desktop"

            # Create desktop file content using DYS_RPI environment variable
            desktop_content = f"""[Desktop Entry]
Name=Start {display_name}
Comment=Switch to {display_name}
Exec=python3 ${DYS_RPI}/scripts/app_switch.py {app_name}
Icon=$HOME/Pictures/icons/{app_name}.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;TV;
"""

            # 1. Create in system applications directory (requires root)
            system_destination = os.path.join(applications_dir, desktop_file)
            try:
                with open(system_destination, 'w') as f:
                    f.write(desktop_content)

                # Set permissions for system file (readable by all, writable by root)
                subprocess.run(["chmod", "644", system_destination], check=True)

                log.info(f"Created system desktop file at {system_destination}")
            except Exception as e:
                log.warning(f"⚠️ Failed to create system desktop file: {e}")
                log.info("Continuing with user desktop file creation...")

            # 2. Create in user's desktop directory
            user_destination = os.path.join(user_desktop_dir, desktop_file)
            try:
                with open(user_destination, 'w') as f:
                    f.write(desktop_content)

                # Set proper ownership and permissions
                subprocess.run(["chown", f"{user}:{user}", user_destination], check=True)
                subprocess.run(["chmod", "755", user_destination], check=True)

                log.info(f"Created user desktop file at {user_destination}")
            except Exception as e:
                log.error(f"Failed to create user desktop file: {e}")
                # Continue anyway, don't return False here

            # 3. Create in root's desktop directory with absolute paths
            root_destination = os.path.join(root_desktop_dir, desktop_file)
            try:
                # Get the absolute path to the project directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_dir = os.path.dirname(script_dir)
                app_switch_path = os.path.join(project_dir, "scripts", "app_switch.py")

                # Create desktop file content with absolute paths for root
                root_desktop_content = f"""[Desktop Entry]
Name=Start {display_name}
Comment=Switch to {display_name}
Exec=python3 {app_switch_path} {app_name}
Icon=/root/Pictures/icons/{app_name}.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;TV;
"""

                # We need to use sudo to write to root's desktop
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(root_desktop_content)
                    temp_path = temp_file.name

                # Copy the temp file to root's desktop using sudo
                subprocess.run(["sudo", "cp", temp_path, root_destination], check=True)

                # Remove the temp file
                os.unlink(temp_path)

                # Set proper permissions
                subprocess.run(["sudo", "chmod", "755", root_destination], check=True)

                # Also copy the icon to root's Pictures/icons directory
                root_icons_dir = "/root/Pictures/icons"
                subprocess.run(["sudo", "mkdir", "-p", root_icons_dir], check=True)

                source_icon = os.path.join(icons_dir, f"{app_name}.png")
                if os.path.exists(source_icon):
                    root_icon_path = os.path.join(root_icons_dir, f"{app_name}.png")
                    subprocess.run(["sudo", "cp", source_icon, root_icon_path], check=True)
                    log.info(f"Copied icon for {app_name} to root's icons directory")

                log.info(f"Created root desktop file at {root_destination}")
            except Exception as e:
                log.error(f"Failed to create root desktop file: {e}")
                # Continue anyway, don't return False here

        log.info("Desktop shortcuts created successfully")
        return True

def ensure_es_systems_config(user):
    """
    Ensure EmulationStation's configuration includes ports and moonlight systems
    """
    es_config_path = "/etc/emulationstation/es_systems.cfg"

    if not os.path.exists(es_config_path):
        log.warning(f"EmulationStation config not found at {es_config_path}")
        return False

    try:
        # Read the current config
        with open(es_config_path, 'r') as f:
            content = f.read()

        # Check if we need to modify the file
        modified = False

        # Check for ports system
        if "<name>ports</name>" not in content:
            log.info("Adding ports system to EmulationStation config")

            # Create ports system definition
            ports_system = f"""  <system>
    <name>ports</name>
    <fullname>Ports</fullname>
    <path>/home/{user}/RetroPie/roms/ports</path>
    <extension>.sh</extension>
    <command>bash %ROM%</command>
    <platform>pc</platform>
    <theme>ports</theme>
  </system>
"""
            # Add before the closing tag
            content = content.replace("</systemList>", ports_system + "</systemList>")
            modified = True


        # Write the updated config if modified
        if modified:
            # Create a backup first
            backup_path = f"{es_config_path}.bak"
            shutil.copy2(es_config_path, backup_path)
            log.info(f"Created backup of EmulationStation config at {backup_path}")

            with open(es_config_path, 'w') as f:
                f.write(content)

            log.info("✅ Updated EmulationStation configuration")

            return True
        else:
            log.info("EmulationStation config already includes ports")
            return True

    except Exception as e:
        log.error(f"Failed to update EmulationStation config: {e}")
        return False


def integrate_with_retropie(gui_apps):
    """Add app switching options to RetroPie's EmulationStation with custom icons"""
    with log.log_section("Integrating with RetroPie"):
        # Get the user from config
        user = config.USER

        # Define the icons directory path
        icons_dir = f"/home/{user}/Pictures/icons"

        # Check if RetroPie is installed
        retropie_roms_path = f"/home/{user}/RetroPie/roms"
        if not os.path.exists(retropie_roms_path):
            log.warning(f"RetroPie roms directory not found at {retropie_roms_path}, skipping integration")
            return False

        # Ensure EmulationStation config includes ports and moonlight systems
        ensure_es_systems_config(user)

        # Create ports directory if it doesn't exist
        ports_path = os.path.join(retropie_roms_path, "ports")
        os.makedirs(ports_path, exist_ok=True)

        # Create a script for each app (except RetroPie itself)
        for app_name, app_config in gui_apps.items():
            if app_name == "retropie":
                continue

            display_name = app_config.get("display_name", app_name)

            # Create the script directly in the ports directory
            script_path = os.path.join(ports_path, f"Launch {display_name}.sh")
            script_content = f"""#!/bin/bash
# Script to launch {display_name} from RetroPie
python3 ${{DYS_RPI}}/scripts/app_switch.py {app_name}
"""

            try:
                with open(script_path, "w") as f:
                    f.write(script_content)

                # Make the script executable
                os.chmod(script_path, 0o755)

                # Set the correct ownership
                subprocess.run(["chown", f"{user}:{user}", script_path], check=True)

                # Copy the custom icon to RetroPie's images directory if it exists
                custom_icon_path = os.path.join(icons_dir, f"{app_name}.png")
                if os.path.exists(custom_icon_path):
                    # RetroPie looks for images in several locations, we'll use the ports images directory
                    retropie_images_dir = os.path.join("/opt/retropie/configs/all/emulationstation/downloaded_images/ports")
                    os.makedirs(retropie_images_dir, exist_ok=True)

                    # Copy the icon with the same name as the script (without .sh)
                    icon_dest = os.path.join(retropie_images_dir, f"Launch {display_name}.png")
                    shutil.copy2(custom_icon_path, icon_dest)

                    # Set the correct ownership
                    subprocess.run(["chown", f"{user}:{user}", icon_dest], check=True)

                    log.info(f"Added custom icon for {display_name} in RetroPie")
                else:
                    # If icon doesn't exist in user's icons directory, try to find it in the project media directory
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    project_dir = os.path.dirname(script_dir)
                    media_dir = os.path.join(project_dir, "media")
                    project_icon_path = os.path.join(media_dir, f"{app_name}.png")

                    if os.path.exists(project_icon_path):
                        # RetroPie looks for images in several locations, we'll use the ports images directory
                        retropie_images_dir = os.path.join("/opt/retropie/configs/all/emulationstation/downloaded_images/ports")
                        os.makedirs(retropie_images_dir, exist_ok=True)

                        # Copy the icon with the same name as the script (without .sh)
                        icon_dest = os.path.join(retropie_images_dir, f"Launch {display_name}.png")
                        shutil.copy2(project_icon_path, icon_dest)

                        # Set the correct ownership
                        subprocess.run(["chown", f"{user}:{user}", icon_dest], check=True)

                        log.info(f"Added custom icon for {display_name} in RetroPie (from project media)")

                log.info(f"Added {display_name} to RetroPie ports")
            except Exception as e:
                log.error(f"Failed to integrate {display_name} with RetroPie: {e}")

        return True

def configure_autostart(gui_apps, boot_app):
    """Configure which application to start on boot using .bashrc"""
    with log.log_section(f"Configuring {boot_app} to start on boot"):
        # Check if the boot app is valid
        if boot_app not in gui_apps:
            log.error(f"Invalid boot app: {boot_app}")
            log.info(f"Valid options are: {', '.join(gui_apps.keys())}")
            return False

        user = config.USER
        bashrc_path = f"/home/{user}/.bashrc"

        # Use the app_switch.sh script from the user's bin directory

        # The line to add to .bashrc using DYS_RPI environment variable
        autostart_line = f"""
# Auto-start application on boot
if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
  python3 ${{DYS_RPI}}/scripts/app_switch.py {boot_app}
fi
"""

        try:
            # Check if .bashrc exists
            if os.path.exists(bashrc_path):
                with open(bashrc_path, "r") as f:
                    content = f.read()

                # Check if app_switch is already in .bashrc (either .sh or .py)
                if "app_switch.sh" in content or "app_switch.py" in content:
                    # Update the existing line
                    new_content = []
                    for line in content.splitlines():
                        if ("app_switch.sh" in line or "app_switch.py" in line) and not line.strip().startswith("#"):
                            # Create a completely new line with the correct path and app name
                            # This ensures consistency regardless of the previous format
                            new_line = f"  python3 ${{DYS_RPI}}/scripts/app_switch.py {boot_app}"
                            log.info(f"🔄 Updating app_switch line in .bashrc to use {boot_app}")
                            new_content.append(new_line)
                        else:
                            new_content.append(line)

                    with open(bashrc_path, "w") as f:
                        f.write("\n".join(new_content))
                    log.info(f"✅ Updated autostart in {bashrc_path}")
                else:
                    # Add the autostart line
                    with open(bashrc_path, "a") as f:
                        f.write(autostart_line)
                    log.info(f"✅ Added autostart to {bashrc_path}")
            else:
                # Create .bashrc with the autostart line
                with open(bashrc_path, "w") as f:
                    f.write(autostart_line)
                log.info(f"✅ Created {bashrc_path} with autostart")

            # Set proper ownership
            subprocess.run(["chown", f"{user}:{user}", bashrc_path], check=True)

            log.info(f"{boot_app} will now start on boot")
            return True
        except Exception as e:
            log.error(f"❌ Failed to configure autostart: {e}")
            return False

def app_switching_submenu():
    """Interactive app switching submenu"""
    while True:
        print("\n=== App Switching Options ===")

        # Get all enabled GUI apps
        gui_apps = get_gui_apps()

        if not gui_apps:
            print("❌ No enabled GUI apps found in configuration")
            print("Please enable at least one GUI app in config.py")
            return

        # Get current boot app
        current_boot_app = getattr(config, "DEFAULT_BOOT_APP", None)
        if not current_boot_app or current_boot_app not in gui_apps:
            current_boot_app = next(iter(gui_apps.keys()))

        print("1) Set up app switching")

        # Check if Kodi is enabled
        if "kodi" in gui_apps:
            print("2) Install Kodi switcher addon")

        print("\nSet boot application:")

        # Create menu options for each GUI app
        app_options = {}
        start_index = 3  # Start after the fixed options
        for i, (app_name, app_config) in enumerate(gui_apps.items(), start_index):
            display_name = app_config.get("display_name", app_name)
            boot_indicator = " (current boot app)" if app_name == current_boot_app else ""
            print(f"{i}) Set {display_name} to start on boot{boot_indicator}")
            app_options[str(i)] = app_name

        print("0) 🔙 Back to Advanced Menu")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            autostart = input(f"Which app should start on boot? ({'/'.join(gui_apps.keys())}) [{current_boot_app}]: ").strip().lower()
            if not autostart:
                autostart = current_boot_app
            if autostart not in gui_apps:
                print(f"❌ Invalid option. Using default ({current_boot_app}).")
                autostart = current_boot_app
            setup_app_switching(autostart)
        elif choice == "2" and "kodi" in gui_apps:
            print("Installing Kodi switcher addon...")
            if install_kodi_addon():
                print("✅ Kodi addon installed successfully")
            else:
                print("❌ Failed to install Kodi addon")
        elif choice in app_options:
            app_name = app_options[choice]
            setup_app_switching(app_name)
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")

def main_install():
    """
    Main installation function for app switching
    Called by the installer
    """
    log.info("🔄 Setting up app switching...")
    autostart = getattr(config, "DEFAULT_BOOT_APP", None)
    success = setup_app_switching(autostart)

    if success:
        log.info("✅ App switching setup completed successfully")
    else:
        log.error("❌ App switching setup failed")

    return success


def main_configure():
    """
    Main configuration function for app switching
    Called by the installer
    """
    # App switching doesn't need additional configuration after installation
    return True


# For testing
if __name__ == "__main__":
    main_install()
