"""
RetroPie Configuration Module

This module handles all configuration tasks for RetroPie, separate from installation.
"""

import os
import shutil
import re
import hashlib
import config
from utils.logger import logger_instance as log
from utils.os_utils import run_command


def is_retropie_installed():
    """Check if RetroPie is installed"""
    return os.path.exists("/opt/retropie/configs")


def get_retropie_version():
    """Get the installed RetroPie version"""
    version_file = "/opt/retropie/VERSION"
    if os.path.exists(version_file):
        try:
            result = run_command(["cat", version_file])
            return result.stdout.strip()
        except Exception:
            return "Version file exists, but could not be read."
    return None


def configure_button_swap():
    """
    Configure A/B button swap in EmulationStation and RetroArch based on config settings
    """
    swap_a_b = getattr(config, "RETROPIE_ES_SWAP_A_B", False)

    # Path to the autoconf.cfg file
    autoconf_path = "/opt/retropie/configs/all/autoconf.cfg"

    if not os.path.exists(os.path.dirname(autoconf_path)):
        log.warning(f"⚠️ RetroPie config directory not found at {os.path.dirname(autoconf_path)}")
        return False

    log.info(f"🎮 Configuring A/B button swap: {'Enabled' if swap_a_b else 'Disabled'}")

    # Convert boolean to the numeric string value expected by RetroPie
    # True -> "1", False -> "0"
    # The value needs to be quoted in the config file
    swap_value = '"1"' if swap_a_b else '"0"'

    # Check if the file exists
    if os.path.exists(autoconf_path):
        # Read the current content
        with open(autoconf_path, "r") as f:
            content = f.readlines()

        # Look for the es_swap_a_b line
        swap_line_found = False
        new_content = []

        for line in content:
            if line.strip().startswith("es_swap_a_b"):
                # Replace the line with the numeric value
                new_content.append(f"es_swap_a_b = {swap_value}\n")
                swap_line_found = True
            else:
                new_content.append(line)

        # If the line wasn't found, add it
        if not swap_line_found:
            new_content.append(f"es_swap_a_b = {swap_value}\n")

        # Write the updated content
        with open(autoconf_path, "w") as f:
            f.writelines(new_content)
    else:
        # Create the file with the setting
        with open(autoconf_path, "w") as f:
            f.write(f"es_swap_a_b = {swap_value}\n")

    log.info(f"✅ A/B button swap configuration {'enabled' if swap_a_b else 'disabled'} in {autoconf_path}")
    return True


def copy_gamepad_configs():
    """
    Copy gamepad configuration files from gamepads_cfg directory to RetroPie's joypad configuration directory
    """
    # Path to the source gamepad configs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    gamepads_cfg_dir = os.path.join(project_dir, "gamepads_cfg")

    # Path to the destination directory
    retropie_joypads_dir = "/opt/retropie/configs/all/retroarch-joypads"

    # Check if source directory exists
    if not os.path.exists(gamepads_cfg_dir):
        log.warning(f"⚠️ Gamepad configs directory not found at {gamepads_cfg_dir}")
        return False

    # Check if destination directory exists
    if not os.path.exists(retropie_joypads_dir):
        log.warning(f"⚠️ RetroPie joypad configs directory not found at {retropie_joypads_dir}")
        return False

    log.info("🎮 Copying gamepad configurations...")

    # Get the user from config
    user = config.USER

    # Copy each config file
    copied_count = 0
    for filename in os.listdir(gamepads_cfg_dir):
        if filename.endswith(".cfg"):
            source_file = os.path.join(gamepads_cfg_dir, filename)
            dest_file = os.path.join(retropie_joypads_dir, filename)

            try:
                # Copy the file
                shutil.copy2(source_file, dest_file)

                # Set proper ownership
                run_command(["chown", f"{user}:{user}", dest_file])

                # Set proper permissions
                run_command(["chmod", "644", dest_file])

                log.info(f"  ✅ Copied {filename} to {retropie_joypads_dir}")
                copied_count += 1
            except Exception as e:
                log.error(f"  ❌ Failed to copy {filename}: {e}")

    if copied_count > 0:
        log.info(f"✅ Successfully copied {copied_count} gamepad configuration files")
    else:
        log.warning("⚠️ No gamepad configuration files were copied")

    return copied_count > 0


def update_retroarch_config(config_file, options, above_include=False):
    """
    Update RetroArch configuration file with the specified options

    Args:
        config_file (str): Path to the RetroArch configuration file
        options (dict): Dictionary of options to set in the configuration file
        above_include (bool): If True, ensure options are placed above the #include line

    Returns:
        bool: True if successful, False otherwise
    """
    if not options:
        log.info(f"ℹ️ No options specified for {config_file}")
        return True

    if not os.path.exists(os.path.dirname(config_file)):
        log.warning(f"⚠️ Directory not found for {config_file}")
        return False

    log.info(f"🔧 Updating RetroArch configuration: {config_file}")

    # Create the file if it doesn't exist
    if not os.path.exists(config_file):
        # For system-specific configs, add the standard header and include
        if above_include:
            with open(config_file, "w") as f:
                f.write("# Settings made here will only override settings in the global retroarch.cfg if placed above the #include line\n\n")

                # Write all options
                for key, value in options.items():
                    f.write(f"{key} = \"{value}\"\n")

                f.write("\n#include \"/opt/retropie/configs/all/retroarch.cfg\"\n")

            log.info(f"✅ Created {config_file} with {len(options)} options")
            return True
        else:
            # For global config, just create an empty file
            with open(config_file, "w") as f:
                f.write("")

    # Read the current content
    with open(config_file, "r") as f:
        content = f.read()

    # For system-specific configs that need options above the include line
    if above_include and "#include" in content:
        lines = content.splitlines()
        include_index = -1

        # Find the include line
        for i, line in enumerate(lines):
            if line.strip().startswith("#include"):
                include_index = i
                break

        if include_index >= 0:
            # Process each option
            for key, value in options.items():
                # Check if the option already exists above the include line
                option_exists = False
                for i in range(include_index):
                    if lines[i].strip().startswith(f"{key} ="):
                        # Update the existing option
                        lines[i] = f"{key} = \"{value}\""
                        option_exists = True
                        log.info(f"  🔄 Updated option: {key} = \"{value}\"")
                        break

                # If the option doesn't exist, add it above the include line
                if not option_exists:
                    lines.insert(include_index, f"{key} = \"{value}\"")
                    include_index += 1  # Adjust the index since we added a line
                    log.info(f"  ➕ Added option: {key} = \"{value}\"")

            # Write the updated content
            with open(config_file, "w") as f:
                f.write("\n".join(lines))

            log.info(f"✅ Updated {config_file} with {len(options)} options above the include line")
            return True
    else:
        # For global config or files without include line, process each option
        modified = False

        for key, value in options.items():
            # Check if the option already exists
            pattern = re.compile(f"^{re.escape(key)}\\s*=\\s*\".*\"", re.MULTILINE)
            if pattern.search(content):
                # Update the existing option
                content = pattern.sub(f"{key} = \"{value}\"", content)
                log.info(f"  🔄 Updated option: {key} = \"{value}\"")
                modified = True
            else:
                # Add the option at the end
                if content and not content.endswith("\n"):
                    content += "\n"
                content += f"{key} = \"{value}\"\n"
                log.info(f"  ➕ Added option: {key} = \"{value}\"")
                modified = True

        # Write the updated content
        if modified:
            with open(config_file, "w") as f:
                f.write(content)

            log.info(f"✅ Updated {config_file} with {len(options)} options")
        else:
            log.info(f"ℹ️ No changes needed for {config_file}")

        return True


def configure_retroarch_options():
    """
    Configure RetroArch options based on config settings
    """
    log.info("🎮 Configuring RetroArch options...")

    # Update global RetroArch options
    if hasattr(config, "RETROPIE_ALL_OPTIONS") and config.RETROPIE_ALL_OPTIONS:
        global_config = "/opt/retropie/configs/all/retroarch.cfg"
        update_retroarch_config(global_config, config.RETROPIE_ALL_OPTIONS)

    # Update system-specific RetroArch options
    if hasattr(config, "RETROPIE_SYSTEM_OPTIONS") and config.RETROPIE_SYSTEM_OPTIONS:
        for system, options in config.RETROPIE_SYSTEM_OPTIONS.items():
            system_config = f"/opt/retropie/configs/{system}/retroarch.cfg"
            update_retroarch_config(system_config, options, above_include=True)

    log.info("✅ RetroArch configuration complete")
    return True


def main():
    """Main configuration function for RetroPie"""
    if not is_retropie_installed():
        log.error("❌ RetroPie is not installed. Please install it first.")
        return False

    log.info("🎮 Configuring RetroPie...")
    
    # Configure button swap
    configure_button_swap()
    
    # Copy gamepad configurations
    copy_gamepad_configs()
    
    # Configure RetroArch options
    configure_retroarch_options()
    
    log.info("✅ RetroPie configuration complete")
    return True


if __name__ == "__main__":
    main()
