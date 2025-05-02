#!/usr/bin/env python3
"""
Update paths in Kodi addon, desktop shortcuts, and RetroPie ports scripts
to use the PROJECT_DIR from config.py
"""

import os
import sys
import shutil
import subprocess

# Add the project root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

import config
from utils.logger import logger_instance as log

def get_app_switch_path():
    """Get the absolute path to the app_switch.sh script"""
    # Format the path with the actual username
    project_dir = config.PROJECT_DIR.format(USER=config.USER)
    return os.path.join(project_dir, "scripts", "app_switch.sh")

def update_kodi_addon():
    """Update the Kodi addon to use the correct path"""
    user = config.USER
    kodi_addon_dir = f"/home/{user}/.kodi/addons/script.switcher"
    main_py_path = os.path.join(kodi_addon_dir, "main.py")
    
    if not os.path.exists(main_py_path):
        log.warning(f"Kodi addon not found at {main_py_path}")
        return False
    
    try:
        # Read the current content
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Replace the hardcoded path with the path from config
        project_dir = config.PROJECT_DIR.format(USER=config.USER)
        old_path = 'project_dir = "/home/tomas/rpi_dys"'
        new_path = f'project_dir = "{project_dir}"'
        
        if old_path in content:
            content = content.replace(old_path, new_path)
            
            # Write the updated content
            with open(main_py_path, 'w') as f:
                f.write(content)
            
            # Set proper ownership
            subprocess.run(["chown", f"{user}:{user}", main_py_path], check=True)
            
            log.info(f"✅ Updated path in Kodi addon: {main_py_path}")
            return True
        else:
            log.warning(f"Could not find path to replace in {main_py_path}")
            return False
    except Exception as e:
        log.error(f"Failed to update Kodi addon: {e}")
        return False

def update_desktop_shortcuts():
    """Update desktop shortcuts to use the correct path"""
    user = config.USER
    app_switch_path = get_app_switch_path()
    
    # Update desktop files in both system and user locations
    applications_dir = "/usr/share/applications"  # System-wide applications
    user_desktop_dir = f"/home/{user}/Desktop"    # User's desktop
    
    updated_count = 0
    
    # Get all desktop files
    desktop_files = []
    if os.path.exists(applications_dir):
        desktop_files.extend([os.path.join(applications_dir, f) for f in os.listdir(applications_dir) if f.endswith(".desktop")])
    if os.path.exists(user_desktop_dir):
        desktop_files.extend([os.path.join(user_desktop_dir, f) for f in os.listdir(user_desktop_dir) if f.endswith(".desktop")])
    
    for desktop_file in desktop_files:
        try:
            # Read the current content
            with open(desktop_file, 'r') as f:
                content = f.read()
            
            # Check if this is one of our desktop files
            if "app_switch.sh" in content:
                # Extract the app name from the Exec line
                app_name = None
                for line in content.splitlines():
                    if line.startswith("Exec=") and "app_switch.sh" in line:
                        parts = line.split()
                        if len(parts) > 1:
                            app_name = parts[-1]
                            break
                
                if not app_name:
                    log.warning(f"Could not extract app name from {desktop_file}")
                    continue
                
                # Create new desktop file content
                display_name = app_name.capitalize()
                for app_name_key, app_config in config.APPLICATIONS.items():
                    if app_name_key == app_name and "display_name" in app_config:
                        display_name = app_config["display_name"]
                        break
                
                desktop_content = f"""[Desktop Entry]
Name=Start {display_name}
Comment=Switch to {display_name}
Exec={app_switch_path} {app_name}
Icon=/home/{user}/Pictures/icons/{app_name}.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;TV;
"""
                
                # Write the updated content
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                
                # Set proper permissions
                if desktop_file.startswith(applications_dir):
                    subprocess.run(["chmod", "644", desktop_file], check=True)
                else:
                    subprocess.run(["chown", f"{user}:{user}", desktop_file], check=True)
                    subprocess.run(["chmod", "755", desktop_file], check=True)
                
                log.info(f"✅ Updated path in desktop file: {desktop_file}")
                updated_count += 1
        except Exception as e:
            log.error(f"Failed to update desktop file {desktop_file}: {e}")
    
    log.info(f"Updated {updated_count} desktop files")
    return updated_count > 0

def update_retropie_ports():
    """Update RetroPie ports scripts to use the correct path"""
    user = config.USER
    app_switch_path = get_app_switch_path()
    
    # Check if RetroPie is installed
    retropie_ports_path = f"/home/{user}/RetroPie/roms/ports"
    if not os.path.exists(retropie_ports_path):
        log.warning(f"RetroPie ports directory not found at {retropie_ports_path}")
        return False
    
    updated_count = 0
    
    # Get all script files
    script_files = [os.path.join(retropie_ports_path, f) for f in os.listdir(retropie_ports_path) if f.endswith(".sh")]
    
    for script_file in script_files:
        try:
            # Read the current content
            with open(script_file, 'r') as f:
                content = f.read()
            
            # Check if this is one of our scripts
            if "app_switch.sh" in content:
                # Extract the app name from the script
                app_name = None
                for line in content.splitlines():
                    if "app_switch.sh" in line:
                        parts = line.split()
                        if len(parts) > 1:
                            app_name = parts[-1]
                            break
                
                if not app_name:
                    log.warning(f"Could not extract app name from {script_file}")
                    continue
                
                # Get the display name from the script filename
                display_name = os.path.basename(script_file).replace("Launch ", "").replace(".sh", "")
                
                # Create new script content
                script_content = f"""#!/bin/bash
# Script to launch {display_name} from RetroPie
{app_switch_path} {app_name}
"""
                
                # Write the updated content
                with open(script_file, 'w') as f:
                    f.write(script_content)
                
                # Set proper permissions
                os.chmod(script_file, 0o755)
                subprocess.run(["chown", f"{user}:{user}", script_file], check=True)
                
                log.info(f"✅ Updated path in RetroPie script: {script_file}")
                updated_count += 1
        except Exception as e:
            log.error(f"Failed to update RetroPie script {script_file}: {e}")
    
    log.info(f"Updated {updated_count} RetroPie scripts")
    return updated_count > 0

def main():
    """Main function"""
    log.info("Updating paths in Kodi addon, desktop shortcuts, and RetroPie ports scripts")
    
    # Update Kodi addon
    update_kodi_addon()
    
    # Update desktop shortcuts
    update_desktop_shortcuts()
    
    # Update RetroPie ports scripts
    update_retropie_ports()
    
    log.info("✅ Path updates completed")
    return True

if __name__ == "__main__":
    main()
