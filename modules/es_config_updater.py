"""
EmulationStation Configuration Updater
Provides functions to update EmulationStation configuration files
"""

import os
import shutil
import xml.etree.ElementTree as ET
from utils.logger import logger_instance as log

def ensure_es_systems_config(user):
    """
    Ensure EmulationStation's configuration includes ports and moonlight systems
    Uses XML parsing for robust modification
    
    Args:
        user: The username to use for file paths
        
    Returns:
        bool: True if successful, False otherwise
    """
    es_config_path = "/etc/emulationstation/es_systems.cfg"
    
    if not os.path.exists(es_config_path):
        log.warning(f"EmulationStation config not found at {es_config_path}")
        return False
    
    try:
        # Create a backup first
        backup_path = f"{es_config_path}.bak"
        shutil.copy2(es_config_path, backup_path)
        log.info(f"Created backup of EmulationStation config at {backup_path}")
        
        # Parse the XML file
        tree = ET.parse(es_config_path)
        root = tree.getroot()
        
        # Check if we need to modify the file
        modified = False
        
        # Check for existing systems
        existing_systems = [system.find('name').text for system in root.findall('system') if system.find('name') is not None]
        
        # Add ports system if it doesn't exist
        if 'ports' not in existing_systems:
            log.info("Adding ports system to EmulationStation config")
            
            # Create ports system element
            ports_system = ET.SubElement(root, 'system')
            
            ET.SubElement(ports_system, 'name').text = 'ports'
            ET.SubElement(ports_system, 'fullname').text = 'Ports'
            ET.SubElement(ports_system, 'path').text = f'/home/{user}/RetroPie/roms/ports'
            ET.SubElement(ports_system, 'extension').text = '.sh'
            ET.SubElement(ports_system, 'command').text = 'bash %ROM%'
            ET.SubElement(ports_system, 'platform').text = 'pc'
            ET.SubElement(ports_system, 'theme').text = 'ports'
            
            modified = True
        
        # Add moonlight system if it doesn't exist
        if 'moonlight' not in existing_systems:
            log.info("Adding moonlight system to EmulationStation config")
            
            # Create moonlight system element
            moonlight_system = ET.SubElement(root, 'system')
            
            ET.SubElement(moonlight_system, 'name').text = 'moonlight'
            ET.SubElement(moonlight_system, 'fullname').text = 'Moonlight Game Streaming'
            ET.SubElement(moonlight_system, 'path').text = f'/home/{user}/RetroPie/roms/moonlight'
            ET.SubElement(moonlight_system, 'extension').text = '.sh'
            ET.SubElement(moonlight_system, 'command').text = 'bash %ROM%'
            ET.SubElement(moonlight_system, 'platform').text = 'pc'
            ET.SubElement(moonlight_system, 'theme').text = 'moonlight'
            
            modified = True
        
        # Write the updated config if modified
        if modified:
            # Convert the XML tree to a string with proper formatting
            xml_str = ET.tostring(root, encoding='unicode')
            
            # Add XML declaration and format the output
            formatted_xml = '<?xml version="1.0"?>\n' + xml_str
            
            # Write the formatted XML to the file
            with open(es_config_path, 'w') as f:
                f.write(formatted_xml)
            
            log.info("✅ Updated EmulationStation configuration")
            
            # Create basic theme files if needed
            create_moonlight_theme(user)
            
            return True
        else:
            log.info("EmulationStation config already includes ports and moonlight systems")
            return True
    
    except Exception as e:
        log.error(f"Failed to update EmulationStation config: {e}")
        return False

def create_moonlight_theme(user):
    """
    Create theme files for Moonlight in all available EmulationStation themes
    
    Args:
        user: The username to use for file paths
    """
    theme_dir = "/etc/emulationstation/themes"
    if not os.path.exists(theme_dir):
        log.warning(f"EmulationStation themes directory not found at {theme_dir}")
        return
    
    try:
        # Find available themes
        themes = [d for d in os.listdir(theme_dir) if os.path.isdir(os.path.join(theme_dir, d))]
        
        for theme in themes:
            # Create moonlight theme directory if it doesn't exist
            moonlight_theme_dir = os.path.join(theme_dir, theme, "moonlight")
            if not os.path.exists(moonlight_theme_dir):
                os.makedirs(moonlight_theme_dir, exist_ok=True)
                
                # Create basic theme.xml
                theme_xml = f"""<theme>
    <formatVersion>3</formatVersion>
    <include>./../{theme}.xml</include>
    <view name="system">
        <text name="systemInfo">
            <string>Moonlight Game Streaming</string>
        </text>
    </view>
</theme>"""
                
                theme_path = os.path.join(moonlight_theme_dir, "theme.xml")
                with open(theme_path, 'w') as f:
                    f.write(theme_xml)
                
                log.info(f"Created basic theme for moonlight in {theme}")
    except Exception as e:
        log.error(f"Failed to create moonlight theme: {e}")
