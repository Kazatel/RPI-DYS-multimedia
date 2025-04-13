from utils.os_utils import get_codename

OS_VERSION = get_codename()

'''
------------------------------------------------------------------------------------
###                               OVERCLOCKING                                   ###
------------------------------------------------------------------------------------
'''
# CPU frequency in MHz (default 2400 for Pi 5)
BOOT_arm_freq = 2800     # Default: 2400

# GPU frequency - sets all GPU-related frequencies together (in MHz)
BOOT_gpu_freq = 950     # Default: 910

# V3D (3D block) frequency in MHz - can be set independently on Pi 5
BOOT_v3d_freq = 950     # Default: 910

# Image sensor pipeline frequency in MHz
BOOT_isp_freq = 950     # Default: 910

# HEVC block frequency in MHz
BOOT_hevc_freq = 950     # Default: 910

# CPU voltage delta in microvolts - recommended over using over_voltage
# Adds offset after DVFS has run
BOOT_over_voltage_delta = 50000  # Example: 50000 for overclocking (adds 0.05V)

# Temperature limit in Celsius - throttles when reached
BOOT_temp_limit = 85  # Max allowed value

# Minimum CPU frequency for dynamic frequency scaling (MHz)
BOOT_arm_freq_min = 1500

# Minimum GPU/V3D frequency (MHz)
BOOT_v3d_freq_min = 500

'''
------------------------------------------------------------------------------------
###                               INSTALLATION                                   ###
------------------------------------------------------------------------------------
'''
# Additional options for installation
# If AUTOMATIC_VERSION_SELECTION is enabled, the script will use the latest available version;
# otherwise, you will be prompted to choose a version
AUTOMATIC_VERSION_SELECTION = True
LOCALE_ALL = "en_US.UTF-8"

'''
------------------------------------------------------------------------------------
###                               APPLICATIONS                                   ###
------------------------------------------------------------------------------------
'''
# Select applications to install
KODI = True             # See KODI_OPTIONS for details
RETROPIE = True
MOONLIGHT = True

'''
------------------------------------------------------------------------------------
###                               KODI_OPTIONS                                   ###
------------------------------------------------------------------------------------
'''
# Specify repositories to configure (list of dictionaries: {'name': '...', 'url': '...'})
KODI_REPOSITORIES = [
    {"name": "CDER", "url": "https://cder.sk/"},
]
