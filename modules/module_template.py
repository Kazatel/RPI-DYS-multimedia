"""
Module Template for RPi-DYS-Multimedia
Use this as a starting point for new application modules
"""

import os
import sys
import config
from utils.logger import logger_instance as log
from utils.os_utils import run_command
from utils.apt_utils import handle_package_install, check_package_installed
from utils.error_handler import handle_error, try_operation
from utils.exceptions import InstallationError, ConfigurationError


# --- CONSTANTS ---
PACKAGE_NAME = "package_name"  # Main package to install
REQUIRED_DEPS = ["dependency1", "dependency2"]  # Required dependencies


# --- INSTALLATION FUNCTIONS ---
def is_installed():
    """
    Check if the application is installed
    
    Returns:
        bool: True if installed, False otherwise
    """
    return check_package_installed(PACKAGE_NAME)


def get_version():
    """
    Get the installed version of the application
    
    Returns:
        str: Version string or None if not installed
    """
    try:
        result, output = run_command(
            ["dpkg-query", "-W", "-f=${Version}", PACKAGE_NAME]
        )
        return output.strip()
    except Exception:
        return None


@handle_error(exit_on_error=False, return_value=False)
def install_prerequisites():
    """
    Install prerequisites for the application
    
    Returns:
        bool: True if successful, False otherwise
    """
    with log.log_section("Installing Prerequisites"):
        log.info(f"📦 Installing dependencies for {PACKAGE_NAME}...")
        
        for dep in REQUIRED_DEPS:
            with try_operation(f"Installing {dep}"):
                success = handle_package_install(dep, auto_update_packages=True)
                if not success:
                    raise InstallationError(f"Failed to install dependency: {dep}")
        
        log.info("✅ All dependencies installed successfully.")
        return True


@handle_error(exit_on_error=False, return_value=False)
def install_application():
    """
    Install the main application
    
    Returns:
        bool: True if successful, False otherwise
    """
    with log.log_section(f"Installing {PACKAGE_NAME}"):
        log.info(f"📦 Installing {PACKAGE_NAME}...")
        
        success = handle_package_install(PACKAGE_NAME, auto_update_packages=config.AUTO_UPDATE_PACKAGES)
        if not success:
            raise InstallationError(f"Failed to install {PACKAGE_NAME}")
        
        log.info(f"✅ {PACKAGE_NAME} installed successfully.")
        return True


# --- CONFIGURATION FUNCTIONS ---
@handle_error(exit_on_error=False, return_value=False)
def configure_application():
    """
    Configure the application after installation
    
    Returns:
        bool: True if successful, False otherwise
    """
    with log.log_section(f"Configuring {PACKAGE_NAME}"):
        log.info(f"🔧 Configuring {PACKAGE_NAME}...")
        
        # Add configuration steps here
        
        log.info(f"✅ {PACKAGE_NAME} configured successfully.")
        return True


# --- MAIN ENTRY POINTS ---
def main_install():
    """
    Main installation function
    Called by the installer
    
    Returns:
        bool: True if successful, False otherwise
    """
    if is_installed():
        version = get_version()
        if version:
            log.info(f"✅ {PACKAGE_NAME} already installed. Version: {version}")
        else:
            log.info(f"✅ {PACKAGE_NAME} already installed.")
            
        if not config.AUTO_UPDATE_PACKAGES:
            return True
        
        log.info(f"🔄 Updating {PACKAGE_NAME}...")
    
    # Install prerequisites
    if not install_prerequisites():
        return False
    
    # Install main application
    if not install_application():
        return False
    
    return True


def main_configure():
    """
    Main configuration function
    Called by the installer
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not is_installed():
        log.error(f"❌ Cannot configure {PACKAGE_NAME}: not installed.")
        return False
    
    return configure_application()


def main():
    """
    Main function when run directly
    """
    log.info(f"🚀 Starting {PACKAGE_NAME} installation and configuration...")
    
    success = main_install()
    if success:
        success = main_configure()
    
    if success:
        log.info(f"✅ {PACKAGE_NAME} setup completed successfully.")
    else:
        log.error(f"❌ {PACKAGE_NAME} setup failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
