# Contributing to RPi-DYS-Multimedia

Thank you for your interest in contributing to RPi-DYS-Multimedia! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Code Style](#code-style)
4. [Testing](#testing)
5. [Error Handling](#error-handling)
6. [Logging](#logging)
7. [Pull Request Process](#pull-request-process)

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rpi-dys-multimedia.git
   cd rpi-dys-multimedia
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Project Structure

The project is organized as follows:

```
RPi-DYS-Multimedia/
├── install.py          # Main script to run system config & app setup
├── config.py           # User-defined settings
├── modules/            # App install + system config modules
│   ├── kodi_install.py
│   ├── retropie_install.py
│   ├── moonlight_install.py
│   ├── system_configuration.py
│   └── module_template.py
├── utils/              # Shared utility logic
│   ├── apt_utils.py
│   ├── os_utils.py
│   ├── interaction.py
│   ├── logger.py
│   ├── error_handler.py
│   ├── exceptions.py
│   └── config_validator.py
├── scripts/            # Utility scripts
│   └── bluetooth_manager.py
├── tests/              # Unit tests
│   ├── test_os_utils.py
│   └── test_config_validator.py
└── README.md
```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use docstrings for all functions, classes, and modules
- Format docstrings according to [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

### Docstring Example

```python
def function_name(param1, param2):
    """
    Brief description of function purpose.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When and why this exception is raised
    """
    # Function implementation
```

## Testing

- Write unit tests for all new functionality
- Place tests in the `tests/` directory
- Name test files with the prefix `test_`
- Run tests with:

```bash
python tests/run_tests.py
```

Or run individual test files:

```bash
python -m unittest tests/test_os_utils.py
```

## Error Handling

- Use the custom exception hierarchy in `utils/exceptions.py`
- Use the error handling decorators from `utils/error_handler.py`
- Be specific about which exceptions you catch
- Always provide meaningful error messages

### Error Handling Example

```python
from utils.error_handler import handle_error
from utils.exceptions import InstallationError

@handle_error(exit_on_error=False, return_value=False)
def install_package(package_name):
    """Install a package with proper error handling"""
    try:
        # Installation code
        if not success:
            raise InstallationError(f"Failed to install {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        raise InstallationError(f"Command failed: {e.cmd}") from e
```

## Logging

- Use the logger from `utils/logger.py`
- Use appropriate log levels (debug, info, warning, error, critical)
- Use log sections for related operations
- Include relevant context in log messages

### Logging Example

```python
from utils.logger import logger_instance as log

# Simple logging
log.info("Starting installation")
log.debug("Detailed information")
log.error("Something went wrong")

# Section logging
with log.log_section("Installing Package"):
    log.info("Step 1: Download")
    # ...
    log.info("Step 2: Configure")
    # ...
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for your changes
4. Ensure all tests pass
5. Update documentation if necessary
6. Submit a pull request with a clear description of the changes

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)

## Questions?

If you have any questions or need help, please open an issue on GitHub or contact the maintainers directly.

Thank you for contributing to RPi-DYS-Multimedia!
