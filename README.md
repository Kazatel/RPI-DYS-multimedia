# 🎮 RPi DYS Multimedia Setup

A fully automated installation and configuration system for setting up a Raspberry Pi as a versatile multimedia center. Designed to be beginner-friendly, customizable, and perfect for retro gaming, streaming, and home entertainment.

---

## 📦 Features

- ✅ **Modular installation** of apps like:
  - **Kodi** – full media center experience
  - **RetroPie** – retro gaming console with controller support
  - **Moonlight** – game streaming from your PC
- 🔄 **App switching integration**:
  - Seamlessly switch between Kodi, RetroPie, and Desktop
  - Desktop shortcuts and service management
  - Custom Kodi addon for switching
- 🎮 **Enhanced controller support**:
  - Bluetooth gamepad pairing and management
  - Xbox controller driver options (xpad/xboxdrv)
  - A/B button swap for RetroPie
- ⚙️ **System configuration automation**:
  - Set system locale and boot options
  - Overclock Raspberry Pi 5 (optional)
  - Mount external drives automatically

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
│   ├── app_switching.py
│   └── system_configuration.py
├── utils/              # Shared utility logic
│   ├── apt_utils.py
│   ├── os_utils.py
│   └── interaction.py
├── scripts/            # Utility scripts
│   └── bluetooth_manager.py
├── addons/             # Kodi addons
│   └── script.switcher/
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

Edit `config.py` to customize your installation:
- Enable/disable applications
- Set overclocking parameters
- Configure controller options
- Add custom Kodi repositories
- Register your Bluetooth gamepads

### 3. Run the installer

```bash
sudo python install.py
```

The installer provides a step-by-step menu:
1. **System Configuration** - locale, boot options, overclocking
2. **Application Installation** - Kodi, RetroPie, Moonlight
3. **Post-Install Configuration** - app-specific settings
4. **App Switching Setup** - integration between applications
5. **Bluetooth Gamepad Setup** - pair and manage controllers
6. **Moonlight Streaming Setup** - NVIDIA GameStream configuration
7. **Advanced Mode** - individual component management
8. **Exit**

---

## 🎮 Controller Configuration

### Bluetooth Gamepads

```bash
# List paired gamepads
sudo python install.py bluetooth list

# Pair a new gamepad
sudo python install.py bluetooth pair

# Connect a specific gamepad
sudo python install.py bluetooth connect <gamepad_name>
```

### Xbox Controller Options

Set in `config.py`:
```python
# Options: None, 'xpad', 'xboxdrv'
GAMEPAD_XBOX_SUPPORT = 'xpad'

# A/B button swap for RetroPie
RETROPIE_ES_SWAP_A_B = False
```

---

## 🔄 App Switching

The system provides multiple ways to switch between applications:

- **Desktop shortcuts** - in the applications menu
- **Kodi addon** - switch directly from within Kodi
- **RetroPie ports** - launch other apps from RetroPie
- **Boot selection** - choose which app starts on boot

Icons for applications are stored in `~/Pictures/icons/`.

---

## 🧠 How It Works

- `install.py` is the main entry point with an interactive menu
- Each application has its own module in the `modules/` directory
- App switching integration manages services and shortcuts
- Bluetooth manager handles controller pairing and connection
- Configuration options in `config.py` control all aspects of the setup

---

## 🐍 Requirements

- Python 3.7+
- Tested on Raspberry Pi OS (Bookworm)
- Raspberry Pi 5 recommended for best performance
- Basic packages are installed automatically

---

## 📜 License

This project is licensed under the MIT License. Do what you want—just don't forget to share back 😄

