import os
import shutil
import hashlib
import re
from utils.apt_utils import handle_package_install
from utils.logger import logger_instance as log
import config
from utils.os_utils import get_home_directory, run_command

HOME_DIR = get_home_directory()
RETROPIE_CLONE_DIR = os.path.join(HOME_DIR, "RetroPie-Setup")


def install_prerequisites():
    log.info("🔧 Installing prerequisites...")
    for pkg in ["git", "lsb-release"]:
        handle_package_install(pkg, auto_update_packages=True)


def clone_retropie():
    log.info("📥 Cloning RetroPie setup script...")
    if not os.path.exists(RETROPIE_CLONE_DIR):
        try:
            run_command(
                ["git", "clone", "--depth=1", "https://github.com/RetroPie/RetroPie-Setup.git", RETROPIE_CLONE_DIR],
                run_as_user=config.APPLICATIONS["retropie"]["user"]
            )
            log.info("✅ Successfully cloned RetroPie-Setup repository.")
        except Exception:
            log.error("❌ Failed to clone RetroPie-Setup repository. See log for details.")
    else:
        log.info("✅ RetroPie-Setup folder already exists. Skipping clone.")


def run_setup_script():
    log.info("🚀 Running RetroPie installation script...")
    user = config.APPLICATIONS["retropie"]["user"]

    script_path = os.path.join(RETROPIE_CLONE_DIR, "retropie_packages.sh")
    setup_path = os.path.join(RETROPIE_CLONE_DIR, "retropie_setup.sh")

    run_command(["chmod", "+x", setup_path, script_path])

    log.tail_note()

    try:
        command = f"cd {RETROPIE_CLONE_DIR} && sudo HOME={config.HOME_DIR} ./retropie_packages.sh setup basic_install"

        run_command(
            command,
            run_as_user=user,
            use_bash_wrapper=True
        )
        log.info("✅ RetroPie installation completed successfully.")
    except Exception as e:
        log.error(f"❌ RetroPie installation failed: {e}")


def is_retropie_installed():
    return os.path.exists("/opt/retropie/configs")


def get_retropie_version():
    version_file = "/opt/retropie/VERSION"
    if os.path.exists(version_file):
        try:
            result = run_command(["cat", version_file])
            return result.stdout.strip()
        except Exception:
            return "Version file exists, but could not be read."
    return None


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


def files_different(file1, file2):
    if not os.path.exists(file2):
        return True
    return calculate_sha256(file1) != calculate_sha256(file2)


def handle_missing_folders(rel_dir):
    src = os.path.join(config.RETROPIE_SOURCE_PATH, rel_dir)
    dst = os.path.join(config.RETROPIE_LOCAL_PATH, rel_dir)

    if not os.path.isdir(src) or not os.path.isdir(dst) or os.path.islink(dst):
        return

    source_subdirs = [d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))]
    local_subdirs = [d for d in os.listdir(dst) if os.path.isdir(os.path.join(dst, d))]
    missing = set(source_subdirs) - set(local_subdirs)

    for subdir in missing:
        src_path = os.path.join(src, subdir)
        dst_path = os.path.join(dst, subdir)
        log.info(f"🔗 Creating missing symlink: {dst_path} → {src_path}")
        os.symlink(src_path, dst_path)


def sync_directory(rel_dir):
    src = os.path.join(config.RETROPIE_SOURCE_PATH, rel_dir)
    dst = os.path.join(config.RETROPIE_LOCAL_PATH, rel_dir)

    log.info(f"📂 Processing: {rel_dir}")

    if not os.path.isdir(src):
        log.warn(f"⚠️ Source directory {src} doesn't exist. Skipping...")
        return

    if os.path.isdir(dst) and not os.path.islink(dst):
        handle_missing_folders(rel_dir)
        for root, _, files in os.walk(dst):
            rel_path = os.path.relpath(root, dst)
            target_dir = os.path.join(src, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            for file in files:
                local_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                if files_different(local_file, target_file):
                    log.info(f"  🔄 Copying: {local_file} → {target_file}")
                    shutil.copy2(local_file, target_file)

        log.info(f"  🔁 Replacing folder with symlink: {dst} → {src}")
        shutil.rmtree(dst)
        os.symlink(src, dst)

    elif not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        log.info(f"  🔗 Creating symlink: {dst} → {src}")
        os.symlink(src, dst)

    elif os.path.islink(dst):
        log.info(f"  ✅ Already symlinked: {dst}")
    else:
        log.warn(f"⚠️ Unexpected state at {dst}. Skipping...")


def sync_retropie_directories():
    if not config.RETROPIE_SOURCE_PATH:
        log.warn("⚠️ RETROPIE_SOURCE_PATH is not set in config. Skipping symlink setup.")
        return

    if not os.path.isdir(config.RETROPIE_SOURCE_PATH):
        log.warn(f"⚠️ Source path {config.RETROPIE_SOURCE_PATH} does not exist or is not mounted.")
        return

    log.info("🔁 Syncing RetroPie directories...")
    for folder in ["BIOS", "retropiemenu", "roms", "splashscreens"]:
        sync_directory(folder)
    log.info("✅ Sync complete.")


def main_install(force=False):
    if is_retropie_installed() and not force:
        version = get_retropie_version()
        if version:
            log.info(f"✅ RetroPie already installed. Version: {version}")
        else:
            log.info("✅ RetroPie already installed.")

        # Even if RetroPie is already installed, we should still apply these configurations
        # Apply Xbox controller driver if specified
        if getattr(config, "GAMEPAD_XBOX_SUPPORT", None):
            install_xbox_controller_driver()

        # Apply A/B button swap configuration
        configure_button_swap()
        return

    install_prerequisites()
    clone_retropie()
    run_setup_script()


def install_xbox_controller_driver():
    """
    Install and configure the selected Xbox controller driver based on config settings
    """
    driver = getattr(config, "GAMEPAD_XBOX_SUPPORT", None)

    if not driver:
        log.info("ℹ️ No Xbox controller driver specified in config. Using default kernel drivers.")
        return

    log.info(f"🎮 Installing Xbox controller driver: {driver}")

    if driver.lower() == 'xpad':
        # Install and configure xpad driver (kernel module)
        try:
            # Check if xpad module is already loaded
            result = run_command(["lsmod | grep xpad"], use_bash_wrapper=True)
            if "xpad" in result.stdout:
                log.info("✅ xpad driver is already loaded.")
            else:
                # Install dkms if needed
                handle_package_install("dkms", auto_update_packages=True)

                # Install xpad driver
                log.info("📦 Installing xpad driver...")
                run_command(["modprobe", "xpad"])

                # Add xpad to /etc/modules to load at boot
                if not os.path.exists("/etc/modules-load.d/xpad.conf"):
                    with open("/etc/modules-load.d/xpad.conf", "w") as f:
                        f.write("xpad\n")
                    log.info("✅ Added xpad to load at boot.")

            log.info("✅ xpad driver setup completed.")
            return True
        except Exception as e:
            log.error(f"❌ Failed to install xpad driver: {e}")
            return False

    elif driver.lower() == 'xboxdrv':
        # Install and configure xboxdrv (userspace driver)
        try:
            # Install xboxdrv package
            log.info("📦 Installing xboxdrv package...")
            success = handle_package_install("xboxdrv", auto_update_packages=True)

            if not success:
                log.error("❌ Failed to install xboxdrv package.")
                return False

            # Create a systemd service to start xboxdrv at boot
            service_content = """[Unit]
Description=Xbox controller driver daemon
After=network.target

[Service]
ExecStart=/usr/bin/xboxdrv --daemon --detach --dbus disabled --silent
Type=forking
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

            with open("/etc/systemd/system/xboxdrv.service", "w") as f:
                f.write(service_content)

            # Enable and start the service
            run_command(["systemctl", "daemon-reload"])
            run_command(["systemctl", "enable", "xboxdrv.service"])
            run_command(["systemctl", "start", "xboxdrv.service"])

            log.info("✅ xboxdrv driver setup completed.")
            return True
        except Exception as e:
            log.error(f"❌ Failed to install xboxdrv driver: {e}")
            return False
    else:
        log.error(f"❌ Unknown Xbox controller driver specified: {driver}")
        log.info("Valid options are: 'xpad', 'xboxdrv'")
        return False


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

    # Update core options
    if hasattr(config, "RETROPIE_CORE_OPTIONS") and config.RETROPIE_CORE_OPTIONS:
        core_options = "/opt/retropie/configs/all/retroarch-core-options.cfg"
        update_retroarch_config(core_options, config.RETROPIE_CORE_OPTIONS)

    # Update system-specific options (these need to be placed above the include line)
    if hasattr(config, "RETROPIE_PSX_OPTIONS") and config.RETROPIE_PSX_OPTIONS:
        psx_config = "/opt/retropie/configs/psx/retroarch.cfg"
        update_retroarch_config(psx_config, config.RETROPIE_PSX_OPTIONS, above_include=True)

    log.info("✅ RetroArch configuration completed")
    return True

def main_configure():
    sync_retropie_directories()
    install_xbox_controller_driver()
    configure_button_swap()
    copy_gamepad_configs()
    configure_retroarch_options()


if __name__ == "__main__":
    main_install(force=True)
    main_configure()
