﻿"""
Configuration file for Raspberry Pi Dys Multimedia Setup
Includes system, installation, overclocking, and app settings.
"""



# ------------------------------------------------------------------------------------
# 🖥️ SYSTEM SETTINGS
# ------------------------------------------------------------------------------------

# Supported OS versions (Debian/Raspbian codenames like 'bookworm', 'bullseye', etc.)
TESTED_OS_VERSION = ['bookworm']  # List of tested OS codenames
TESTED_MODELS = ['Raspberry Pi 5 Model B Rev 1.0']
ON_OWN_RISK = False  # Allow running on untested hardware or OS


# Default user and log location
USER = 'tomas'
HOME_DIR = '/home/{USER}'
LOG_DIR = '/home/{USER}/.local/share/rpi_dys/logs'  # User-writable log directory





# ------------------------------------------------------------------------------------
# 🚀 OVERCLOCKING SETTINGS
# ------------------------------------------------------------------------------------
"""
Overclocking Settings (All frequencies are stated in MHz)
⚠️ Modify with caution. Stability depends on your Raspberry Pi model and cooling.

Recommended for Pi 5 only unless you're familiar with your board's limitations.
"""

# CPU (ARM) frequency
BOOT_arm_freq = 2800         # Default: 2400

# GPU composite frequency
BOOT_gpu_freq = 950          # Default: 910

# 3D (v3d) block frequency
BOOT_v3d_freq = 950          # Default: 910

# Image signal processor frequency
BOOT_isp_freq = 950          # Default: 910

# HEVC decoder block frequency
BOOT_hevc_freq = 950         # Default: 910

# Additional CPU voltage in microvolts (e.g. 50000 = +0.05V)
BOOT_over_voltage_delta = 50000  # Use only on supported models (Pi 4/5)

# Maximum CPU temp in Celsius before throttling
BOOT_temp_limit = 85

# Minimum CPU and V3D frequencies for dynamic scaling
BOOT_arm_freq_min = 1500
BOOT_v3d_freq_min = 500

# ------------------------------------------------------------------------------------
# ⚡ LEGACY VOLTAGE OPTIONS (for Pi 1 / Pi 2 / Pi 3)
# [source:https://github.com/raspberrypi/documentation/blob/develop/documentation/asciidoc/computers/config_txt/overclocking.adoc]
# ------------------------------------------------------------------------------------
# Uncomment these if you're experimenting with older models that don't support newer over_voltage_delta settings

# BOOT_over_voltage = 0                    # CPU/GPU core voltage offset (default: 0 = ~1.35V / 1.2V on Pi 1)
# BOOT_over_voltage_min = 0                # Minimum voltage for DVFS scaling (default: 0 = ~1.2V)

# BOOT_over_voltage_sdram = 0              # General SDRAM voltage (default: 0 = ~1.2V)
# BOOT_over_voltage_sdram_c = 0            # SDRAM controller voltage (default: 0 = ~1.2V)
# BOOT_over_voltage_sdram_i = 0            # SDRAM I/O voltage (default: 0 = ~1.2V)
# BOOT_over_voltage_sdram_p = 0            # SDRAM PHY voltage (default: 0 = ~1.2V)


"""
DEFAULT FREQUENCIES BY MODEL (MHz)
[Source:https://github.com/raspberrypi/documentation/blob/develop/documentation/asciidoc/computers/config_txt/overclocking.adoc]
------------------------------------------------------------------------------------------------------------------------------------
| Option           | Pi 0/W | Pi1  | Pi2  | Pi3  | Pi3A+/Pi3B+ | CM4 & Pi4B <= R1.3 | Pi4B R1.4     | Pi 400 | Pi Zero 2 W  | Pi 5  |
|------------------|--------|------|------|------|-------------|--------------------|---------------|--------|--------------|-------|
| arm_freq         | 1000   | 700  | 900  | 1200 | 1400        | 1500               | 1500/1800     | 1800   | 1000         | 2400  |
| core_freq        | 400    | 250  | 250  | 400  | 400         | 500                | 500           | 500    | 400          | 910   |
| h264_freq        | 300    | 250  | 250  | 400  | 400         | 500                | 500           | 500    | 300          | N/A   |
| isp_freq         | 300    | 250  | 250  | 400  | 400         | 500                | 500           | 500    | 300          | 910   |
| v3d_freq         | 300    | 250  | 250  | 400  | 400         | 500                | 500           | 500    | 300          | 910   |
| hevc_freq        | N/A    | N/A  | N/A  | N/A  | N/A         | 500                | 500           | 500    | N/A          | 910   |
| sdram_freq       | 450    | 400  | 450  | 450  | 500         | 3200               | 3200          | 3200   | 450          | 4267  |
| arm_freq_min     | 700    | 700  | 600  | 600  | 600         | 600                | 600           | 600    | 600          | 1500  |
| core_freq_min    | 250    | 250  | 250  | 250  | 250         | 200                | 200           | 200    | 250          | 500   |
| gpu_freq_min     | 250    | 250  | 250  | 250  | 250         | 250                | 250           | 250    | 250          | 500   |
| h264_freq_min    | 250    | 250  | 250  | 250  | 250         | 250                | 250           | 250    | 250          | N/A   |
| isp_freq_min     | 250    | 250  | 250  | 250  | 250         | 250                | 250           | 250    | 250          | 500   |
| v3d_freq_min     | 250    | 250  | 250  | 250  | 250         | 250                | 250           | 250    | 250          | 500   |
| sdram_freq_min   | 400    | 400  | 400  | 400  | 400         | 3200               | 3200          | 3200   | 400          | 4267  |
-------------------------------------------------------------------------------------------------------------------------------------
"""


# ------------------------------------------------------------------------------------
# ⚙️ INSTALLATION OPTIONS
# ------------------------------------------------------------------------------------

# If True, automatically selects the latest version during installs
AUTO_UPDATE_PACKAGES = True

# Locale setting
LOCALE_ALL = "en_US.UTF-8"

# Bash alias defaults
BASH_ALIASES = """
alias ll='ls -l'
alias la='ls -a'
alias lah='ls -lah'
alias l='ls -CF'

# Bluetooth gamepad connection aliases - only created if DYS_RPI is set
if [ -n "${DYS_RPI}" ]; then
    # Standard connection (interactive approach)
    alias btc='python3 ${DYS_RPI}/scripts/bluetooth_manager.py connect'

    # Direct connection (better for SSH remote sessions)
    alias btbc='python3 ${DYS_RPI}/scripts/bluetooth_manager.py bconnect'

    # Status and list commands
    alias bts='python3 ${DYS_RPI}/scripts/bluetooth_manager.py status'
    alias btl='python3 ${DYS_RPI}/scripts/bluetooth_manager.py list'

    # Pairing command
    alias btp='python3 ${DYS_RPI}/scripts/bluetooth_manager.py pair'
fi
"""

# Disk mount configuration (used to generate /etc/fstab entries)
DISKS = [
    {'name': 'Retropie', 'mountpoint': '/mnt/retropie'},
    {'name': 'torrent', 'mountpoint': '/mnt/torrent'},
]


# ------------------------------------------------------------------------------------
# 📦 APPLICATION SELECTION
# ------------------------------------------------------------------------------------

# Set to True to enable installing each application
APPLICATIONS = {
    "kodi": {
        "enabled": True,
        "user": USER,
        "type": "GUI",
        "display_name": "Kodi Media Center"
    },
    "retropie": {
        "enabled": True,
        "user": USER,  # ✅ this should *not* be root
        "type": "GUI",
        "display_name": "RetroPie"
    },
    "desktop": {
        "enabled": True,
        "user": USER,
        "type": "GUI",
        "display_name": "Desktop Environment"
    },
    "moonlight": {
        "enabled": True,
        "user": USER,
        "type": "SERVICE",  # Not a GUI app that needs exclusive display access
        "display_name": "Moonlight Streaming"
    }
}

# Default app to boot into (must be one of the enabled apps with type "GUI")
DEFAULT_BOOT_APP = "kodi"


# ------------------------------------------------------------------------------------
# 🎬 KODI CONFIGURATION
# ------------------------------------------------------------------------------------

# Kodi add-on repositories to configure
KODI_REPOSITORIES = [
    {"name": "CDER", "url": "https://cder.sk/"},
    {"name": "cache-sk", "url": "https://cache-sk.github.io/kodirepo/"},
    {"name": "otaku", "url": "https://goldenfreddy0703.github.io/repository.otaku"},
    {"name": "crew", "url": "https://team-crew.github.io"},
]

# Location of Kodi's sources.xml for repo import
KODI_REPOSITORY_FILE_PATH = f'/home/{USER}/.kodi/userdata/sources.xml'


# ------------------------------------------------------------------------------------
# 🎮 RETROPIE CONFIGURATION
# ------------------------------------------------------------------------------------

# Where RetroPie installs and stores configs/ROMs locally
RETROPIE_LOCAL_PATH = f"/home/{USER}/RetroPie/"
#RETROPIE_LOCAL_PATH = f"/root/RetroPie/"

# External mount source path for ROMs, BIOS, splashscreens, etc.
# The folder structure inside this path should mirror the structure of the local RetroPie directory.
RETROPIE_SOURCE_PATH = "/mnt/retropie/"


GAMEPADS = {
    'white_new': '83:24:11:04:0F:19',
    'black_new': '83:10:0D:12:51:D6',
    'white_old': '6A:21:21:50:63:25',
    'black_old': 'A7:0E:21:50:63:25',
}

# Xbox controller driver support
# Options: None, 'xpad', 'xboxdrv'
# - None: Use default kernel drivers
# - 'xpad': Use the xpad driver (kernel module)
# - 'xboxdrv': Use the xboxdrv userspace driver
GAMEPAD_XBOX_SUPPORT = 'xpad'

# Swap A/B buttons in EmulationStation and RetroArch
# Set to True to swap A/B buttons (useful for Nintendo-style controllers)
# DEFAULT: False
RETROPIE_ES_SWAP_A_B = True


# RetroArch core options configuration file
# Path: /opt/retropie/configs/all/retroarch-core-options.cfg
# These options control specific emulator core behaviors
RETROPIE_CORE_OPTIONS = {
    # PCSX ReARMed PlayStation emulator enhancement options
    # DEFAULT: "disabled"
    "pcsx_rearmed_neon_enhancement_enable": "disabled",

    # PCSX ReARMed enhancement for non-main elements
    # DEFAULT: "disabled"
    "pcsx_rearmed_neon_enhancement_no_main": "disabled"
}

# PlayStation-specific RetroArch configuration
# Path: /opt/retropie/configs/psx/retroarch.cfg
# These options only apply to PlayStation emulation
RETROPIE_PSX_OPTIONS = {
    # Enable video smoothing for PlayStation games
    # DEFAULT: "option not presented"
    "video_smooth": "true"
}

# Global RetroArch configuration for all emulators
# Path: /opt/retropie/configs/all/retroarch.cfg
# These options apply to all emulated systems
RETROPIE_ALL_OPTIONS = {
    # Aspect ratio index (20 = custom aspect ratio)
    # DEFAULT: 0 (4:3)
    # 22 (16:9)
    "aspect_ratio_index": 20
}
