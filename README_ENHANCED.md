# 🎮 RPi DYS Multimedia Setup

A fully automated installation and configuration system for setting up a Raspberry Pi as a versatile multimedia center. Designed to be beginner-friendly, customizable, and perfect for retro gaming, streaming, and home entertainment.

---

## 📦 Features

- ✅ **Modular installation** of apps like:
  - **Kodi** – full media center experience
  - **RetroPie** – retro gaming console with controller support
  - **Moonlight** – game streaming from your PC
- ⚙️ **System configuration automation**:
  - Set system locale
  - Overclock Raspberry Pi 5 (optional)
- 🎮 **Gamepad pairing automation**
  - Bluetooth auto-connector based on gamepad name
  - Interactive pairing with timeout handling
  - Gamepad status monitoring
- 🛠️ **Robust architecture**:
  - Comprehensive error handling
  - Detailed logging system
  - Configuration validation
  - Unit testing framework
- 🧩 **Developer-friendly**:
  - Consistent module interfaces
  - Well-documented codebase
  - Contributor guidelines

---

## 📁 Project Structure

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

---

## 🚀 Quick Start

### 1. Clone this repo

```bash
git clone https://github.com/yourusername/rpi-dys-multimedia.git
cd rpi-dys-multimedia
```

### 2. Configure your setup

Edit `config.py` to:
- Enable/disable apps
- Set overclocking parameters
- Add custom Kodi repositories
- Define Bluetooth gamepads

### 3. Run the installer

To run in interactive mode:
```bash
sudo python install.py
```

To run specific commands:
```bash
# System configuration
sudo python install.py system

# Install applications
sudo python install.py apps
sudo python install.py apps --app=kodi  # Install specific app

# Configure applications
sudo python install.py config

# Bluetooth operations
sudo python install.py bluetooth list
sudo python install.py bluetooth pair
sudo python install.py bluetooth connect <gamepad_name>
```

## ⚙️ Configuration Overview

### Enable or disable apps
```python
# config.py
APPLICATIONS = {
    "kodi": {
        "enabled": True,
        "user": "root" 
    },
    "retropie": {
        "enabled": True,
        "user": "pi"
    },
    "moonlight": {
        "enabled": True,
        "user": "root"
    }
}
```

### Overclocking options
```python
# config.py
BOOT_arm_freq = 2800
BOOT_gpu_freq = 950
BOOT_over_voltage_delta = 50000
```

### Register your gamepads
```python
# config.py
GAMEPADS = {
    "black_old": "01:10:0D:12:51:D6",
    "black_new": "A7:0E:21:50:63:25",
    "white_new": "6A:21:21:50:63:25",
    "white_old": "01:24:11:04:0F:19"
}
```

## 🧠 How It Works

- `install.py` is the main entry point
- Based on mode, it calls:
  - `apply_locale_settings()` and `apply_boot_config()` from `system_configuration.py`
  - Installs selected apps by dynamically loading their modules
- Utility functions handle all APT package logic, user prompts, and Bluetooth pairing
- Error handling and logging provide robust operation

## 🎮 Bluetooth Gamepad Management

The enhanced Bluetooth manager provides:

- **Improved pairing process** with proper timeout handling
- **Automatic recognition** of gamepads from your config
- **Status monitoring** to check connection state
- **Interactive mode** for easy pairing of new devices

Commands:
```bash
# List all configured gamepads and their status
python scripts/bluetooth_manager.py list

# Pair a new gamepad
python scripts/bluetooth_manager.py pair

# Connect a specific gamepad
python scripts/bluetooth_manager.py connect black_new

# Check status of a gamepad
python scripts/bluetooth_manager.py status black_new
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python tests/run_tests.py
```

Or run individual test files:

```bash
python -m unittest tests/test_os_utils.py
```

## 🤝 Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## 💡 Tips

- Reboot is recommended after running in system mode
- You can run `scripts/bluetooth_manager.py` to connect gamepads by name
- Use `AUTO_UPDATE_PACKAGES = True` in config.py to automatically update installed packages

## 🐍 Requirements

- Python 3.7+
- Tested on Raspberry Pi OS (Bookworm, Bullseye)
- Basic packages are installed automatically (e.g., git, lsb-release)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
