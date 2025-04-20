"""
Configuration file for Raspberry Pi Dys Multimedia Setup
Includes system, installation, overclocking, and app settings.
"""

from utils.os_utils import (get_home_directory,get_username)

# ------------------------------------------------------------------------------------
# 🖥️ SYSTEM SETTINGS
# ------------------------------------------------------------------------------------

# Supported OS versions (Debian/Raspbian codenames like 'bookworm', 'bullseye', etc.)
TESTED_OS_VERSION = ['bookworm']  # List of tested OS codenames
TESTED_MODELS = ['Raspberry Pi 5 Model B Rev 1.0']
ON_OWN_RISK = False  # Allow running on untested hardware or OS


# Default user and log location
USER = get_username()
HOME_DIR = get_home_directory()
LOG_DIR = '/var/log/'  # Log file: rpi_dys_multimedia.log




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
alias l='ls -CF'
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
        "user": "root" 
    },
    "retropie": {
        "enabled": True,
        "user": USER  # ✅ this should *not* be root
    },
    "moonlight": {
        "enabled": True,
        "user": "root"
    }
}


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
    'black_old': '01:10:0D:12:51:D6',
    'black_new': 'A7:0E:21:50:63:25',
    'white_new': '6A:21:21:50:63:25',
    'white_old': '01:24:11:04:0F:19'
}