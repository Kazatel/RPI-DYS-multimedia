"""
Centralized error handling for RPi-DYS-Multimedia
Provides decorators and utilities for consistent error handling
"""

import functools
import traceback
import sys
from utils.logger import logger_instance as log
from utils.exceptions import RPiDysError


def handle_error(exit_on_error=False, return_value=False):
    """
    Decorator for centralized error handling
    
    Args:
        exit_on_error: If True, exit the program on error
        return_value: Value to return on error (if not exiting)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RPiDysError as e:
                # Known error from our exception hierarchy
                log.error(f"{type(e).__name__}: {str(e)}")
                
                if exit_on_error:
                    log.error("Exiting due to error.")
                    sys.exit(1)
                return return_value
            except Exception as e:
                # Unexpected error
                log.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
                log.debug(f"Exception details:\n{traceback.format_exc()}")
                
                if exit_on_error:
                    log.error("Exiting due to unexpected error.")
                    sys.exit(1)
                return return_value
        return wrapper
    return decorator


def try_operation(operation_name):
    """
    Context manager for error handling
    
    Args:
        operation_name: Name of the operation for logging
        
    Example:
        with try_operation("Installing package"):
            install_package()
    """
    class OperationContext:
        def __init__(self, name):
            self.name = name
            
        def __enter__(self):
            log.info(f"Starting: {self.name}")
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                log.info(f"Completed: {self.name}")
                return False
                
            if issubclass(exc_type, RPiDysError):
                log.error(f"Error in {self.name}: {exc_val}")
            else:
                log.error(f"Unexpected error in {self.name}: {exc_val}")
                log.debug(f"Exception details:\n{traceback.format_exc()}")
                
            return True  # Suppress the exception
            
    return OperationContext(operation_name)


def safe_function(func):
    """
    Decorator that catches all exceptions and logs them
    but never crashes the program
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that never raises exceptions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(f"Error in {func.__name__}: {str(e)}")
            log.debug(f"Exception details:\n{traceback.format_exc()}")
            return None
    return wrapper
