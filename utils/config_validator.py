"""
Configuration validation utilities for RPi-DYS-Multimedia
Ensures that the configuration is valid before proceeding with installation
"""

import os
from utils.logger import logger_instance as log
from utils.exceptions import ValidationError, ConfigurationError


def validate_config(config):
    """
    Validate configuration settings
    
    Args:
        config: Configuration module to validate
        
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    errors = []
    warnings = []
    
    # Check required settings
    if not hasattr(config, 'USER') or not config.USER:
        errors.append("USER must be set in config.py")
    
    # Check application settings
    if not hasattr(config, 'APPLICATIONS') or not config.APPLICATIONS:
        errors.append("No applications configured in APPLICATIONS")
    else:
        # Check each application's configuration
        for app_name, app_config in config.APPLICATIONS.items():
            if not isinstance(app_config, dict):
                errors.append(f"Application '{app_name}' configuration must be a dictionary")
                continue
                
            if "enabled" not in app_config:
                warnings.append(f"Application '{app_name}' is missing 'enabled' key")
                
            if "user" not in app_config:
                warnings.append(f"Application '{app_name}' is missing 'user' key")
    
    # Check for valid paths
    for app_name, app_config in getattr(config, 'APPLICATIONS', {}).items():
        if app_name == "retropie" and app_config.get("enabled", False):
            if not hasattr(config, 'RETROPIE_LOCAL_PATH') or not config.RETROPIE_LOCAL_PATH:
                errors.append("RETROPIE_LOCAL_PATH must be set when RetroPie is enabled")
                
            if hasattr(config, 'RETROPIE_SOURCE_PATH') and config.RETROPIE_SOURCE_PATH:
                if not os.path.exists(config.RETROPIE_SOURCE_PATH):
                    warnings.append(f"RETROPIE_SOURCE_PATH '{config.RETROPIE_SOURCE_PATH}' does not exist")
    
    # Check system settings
    if not hasattr(config, 'TESTED_OS_VERSION') or not config.TESTED_OS_VERSION:
        warnings.append("TESTED_OS_VERSION is not set. All OS versions will be considered untested.")
        
    if not hasattr(config, 'TESTED_MODELS') or not config.TESTED_MODELS:
        warnings.append("TESTED_MODELS is not set. All Raspberry Pi models will be considered untested.")
    
    # Check log directory
    if hasattr(config, 'LOG_DIR') and config.LOG_DIR:
        if not os.path.exists(config.LOG_DIR) and not os.access(os.path.dirname(config.LOG_DIR), os.W_OK):
            warnings.append(f"LOG_DIR '{config.LOG_DIR}' does not exist and may not be writable")
    
    # Report warnings
    for warning in warnings:
        log.warning(f"Configuration warning: {warning}")
    
    # Report errors
    if errors:
        for error in errors:
            log.error(f"Configuration error: {error}")
        raise ConfigurationError("Invalid configuration. See log for details.")
    
    return True


def validate_user_exists(username):
    """
    Validate that a user exists on the system
    
    Args:
        username: Username to validate
        
    Returns:
        bool: True if user exists
        
    Raises:
        ValidationError: If user does not exist
    """
    import pwd
    
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        raise ValidationError(f"User '{username}' does not exist on the system")


def validate_path_exists(path, create=False, is_dir=True):
    """
    Validate that a path exists
    
    Args:
        path: Path to validate
        create: If True, create the path if it doesn't exist
        is_dir: If True, path should be a directory
        
    Returns:
        bool: True if path exists or was created
        
    Raises:
        ValidationError: If path does not exist and could not be created
    """
    if os.path.exists(path):
        if is_dir and not os.path.isdir(path):
            raise ValidationError(f"Path '{path}' exists but is not a directory")
        elif not is_dir and os.path.isdir(path):
            raise ValidationError(f"Path '{path}' exists but is a directory, not a file")
        return True
    
    if create:
        try:
            if is_dir:
                os.makedirs(path, exist_ok=True)
            else:
                # Create parent directory for file
                parent_dir = os.path.dirname(path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                # Create empty file
                with open(path, 'w') as f:
                    pass
            return True
        except OSError as e:
            raise ValidationError(f"Could not create path '{path}': {str(e)}")
    
    raise ValidationError(f"Path '{path}' does not exist")


def validate_command_exists(command):
    """
    Validate that a command exists on the system
    
    Args:
        command: Command to validate
        
    Returns:
        bool: True if command exists
        
    Raises:
        ValidationError: If command does not exist
    """
    import shutil
    
    if shutil.which(command):
        return True
    
    raise ValidationError(f"Command '{command}' not found in PATH")
