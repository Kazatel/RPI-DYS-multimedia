"""
Custom exception hierarchy for RPi-DYS-Multimedia
Provides structured error handling and categorization
"""

class RPiDysError(Exception):
    """Base exception for all RPi-DYS-Multimedia errors"""
    pass


class InstallationError(RPiDysError):
    """Error during application installation"""
    pass


class ConfigurationError(RPiDysError):
    """Error during system or application configuration"""
    pass


class SystemError(RPiDysError):
    """Error related to system operations"""
    pass


class BluetoothError(RPiDysError):
    """Error related to Bluetooth operations"""
    pass


class ValidationError(RPiDysError):
    """Error related to validation of inputs or configuration"""
    pass


class FileSystemError(RPiDysError):
    """Error related to file system operations"""
    pass


class NetworkError(RPiDysError):
    """Error related to network operations"""
    pass


class UserInputError(RPiDysError):
    """Error related to user input"""
    pass
