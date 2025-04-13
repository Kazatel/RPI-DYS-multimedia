# 🎮 RPi DYS Multimedia Setup

NOTE: Project is unfinished !!!

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
- 🛠️ Structured with maintainability in mind:
  - Separated `modules/` for app installs
  - `utils/` for shared logic (APT, interaction, OS tools)
  - `scripts/` for utility helpers like gamepad pairing

---

## 📁 Project Structure

RPi-DYS-Multimedia/
├── install.py          # Main script to run system config & app setup
├── config.py           # User-defined settings
├── modules/            # App install + system config modules
│   ├── kodi_install.py
│   ├── retropie_install.py
│   ├── moonlight_install.py
│   └── system_configuration.py
├── utils/              # Shared utility logic
│   ├── apt_utils.py
│   ├── os_utils.py
│   └── interaction.py
├── scripts/            # Utility scripts (e.g., for gamepad management)
│   └── bluetooth_manager.py
└── README.md


---

## 🚀 Quick Start

### 1. Clone this repo

```bash
git clone [https://github.com/yourusername/rpi-dys-multimedia.git](https://github.com/yourusername/rpi-dys-multimedia.git)
cd rpi-dys-multimedia
```
2. Configure your setup

Edit config.py to:

    Enable/disable apps
    Set overclocking parameters
    Add custom Kodi repositories
    Define Bluetooth gamepads

3. Run the installer

To run everything:
```bash
python3 install.py
```
To run only system configuration (locale, overclocking, etc.):

```bash
python3 install.py system
```
To install applications only:
```bash
python3 install.py apps
```
⚙️ Configuration Overview

Enable or disable apps
Python

# config.py
KODI = True
RETROPIE = True
MOONLIGHT = True

Overclocking options
Python

# config.py
BOOT_arm_freq = 2800
BOOT_gpu_freq = 950
BOOT_over_voltage_delta = 50000

Add Kodi repositories
Python

KODI_REPOSITORIES = [
    {"name": "CDER", "url": "[https://cder.sk/](https://cder.sk/)"}
]

Register your gamepads
Python

GAMEPADS = {
    "my_gamepad": "AA:BB:CC:DD:EE:FF",
    "backup_controller": "11:22:33:44:55:66"
}

🧠 How It Works

    install.py is the main entry point
    Based on mode, it calls:
        apply_locale_settings() and apply_overclock_settings() from system_configuration.py
        Installs selected apps by dynamically loading their modules
    Utility functions handle all APT package logic, user prompts, and Bluetooth pairing

💡 Tips

    Reboot is recommended after running in system mode
    You can run scripts/bluetooth_manager.py to connect gamepads by name
    Use AUTOMATIC_VERSION_SELECTION = True in config.py to skip manual version selection

🐍 Requirements

    Python 3.7+
    Tested on Raspberry Pi OS (Bookworm, Bullseye)
    Basic packages are installed automatically (e.g., git, lsb-release)

📜 License

This project is licensed under the MIT License. Do what you want—just don't forget to share back 😄
🤝 Contributing

