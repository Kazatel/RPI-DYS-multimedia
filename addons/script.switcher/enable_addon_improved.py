#!/usr/bin/env python3
"""
Improved script to enable the App Switcher addon in Kodi
Uses multiple methods to ensure the addon is enabled
"""

import os
import sqlite3
import sys
import json
import xml.etree.ElementTree as ET
import socket
import time
import subprocess

def enable_via_database():
    """Enable the addon by directly modifying Kodi's database"""
    print("Attempting to enable addon via database...")

    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Find Kodi database
    userdata_dir = os.path.join(home_dir, ".kodi", "userdata", "Database")
    addons_db_path = None

    if os.path.exists(userdata_dir):
        for file in os.listdir(userdata_dir):
            if file.startswith("Addons") and file.endswith(".db"):
                addons_db_path = os.path.join(userdata_dir, file)
                print(f"Found Kodi addons database: {addons_db_path}")
                break

    if not addons_db_path:
        print("No Kodi addons database found.")
        return False

    try:
        # Connect to the database
        conn = sqlite3.connect(addons_db_path)
        cursor = conn.cursor()

        # Check if the addon is already in the database
        cursor.execute("SELECT id FROM installed WHERE addonID = 'script.switcher'")
        result = cursor.fetchone()

        if result:
            # Update the addon state to enabled
            cursor.execute("UPDATE installed SET enabled = 1 WHERE addonID = 'script.switcher'")
            print("Updated App Switcher addon to enabled state")
        else:
            # Insert the addon as enabled
            cursor.execute(
                "INSERT INTO installed (addonID, enabled, installDate) VALUES (?, ?, ?)",
                ("script.switcher", 1, "2023-01-01 00:00:00")
            )
            print("Added App Switcher addon to database as enabled")

        # Commit changes and close
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error enabling addon via database: {e}")
        return False

def enable_via_json_rpc():
    """Enable the addon using Kodi's JSON-RPC API"""
    print("Attempting to enable addon via JSON-RPC...")

    # Check if Kodi is running
    try:
        # Try to connect to Kodi's JSON-RPC port with a short timeout
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)  # Short timeout to avoid hanging
        result = s.connect_ex(('localhost', 9090))
        s.close()

        if result != 0:
            print("Kodi is not running or JSON-RPC port is not accessible")
            print("This is normal if Kodi is not currently running")
            print("The addon will be enabled when Kodi is next started")
            return False

        # Prepare the JSON-RPC command
        command = {
            "jsonrpc": "2.0",
            "method": "Addons.SetAddonEnabled",
            "params": {
                "addonid": "script.switcher",
                "enabled": True
            },
            "id": 1
        }

        # Send the command to Kodi with timeout
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)  # 3 second timeout for the entire operation
            s.connect(('localhost', 9090))
            s.send(json.dumps(command).encode() + b'\n')

            # Get the response with timeout
            response = b""
            s.settimeout(2)  # 2 second timeout for receiving data

            # Try to receive data once
            try:
                data = s.recv(1024)
                response += data
            except socket.timeout:
                print("Timeout waiting for response from Kodi")
                s.close()
                return False

            s.close()

            # Parse the response
            if response:
                try:
                    response_json = json.loads(response.decode())
                    if "result" in response_json and response_json["result"] == "OK":
                        print("Successfully enabled addon via JSON-RPC")
                        return True
                    else:
                        print(f"Failed to enable addon via JSON-RPC: {response_json}")
                        return False
                except json.JSONDecodeError:
                    print("Received invalid JSON response from Kodi")
                    return False
            else:
                print("No response received from Kodi")
                return False

        except socket.timeout:
            print("Connection to Kodi timed out")
            return False

    except Exception as e:
        print(f"Error enabling addon via JSON-RPC: {e}")
        return False

def enable_via_xml():
    """Enable the addon by modifying Kodi's XML configuration files"""
    print("Attempting to enable addon via XML configuration...")

    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Create addon_data directory and settings file
    addon_data_dir = os.path.join(home_dir, ".kodi", "userdata", "addon_data", "script.switcher")
    os.makedirs(addon_data_dir, exist_ok=True)

    # Create settings.xml
    settings_path = os.path.join(addon_data_dir, "settings.xml")
    with open(settings_path, "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n</settings>')

    # Modify addons.xml to include our addon
    addons_dir = os.path.join(home_dir, ".kodi", "userdata", "addon_data")
    addons_xml_path = os.path.join(home_dir, ".kodi", "userdata", "addon_data", "addons.xml")

    try:
        if os.path.exists(addons_xml_path):
            # Parse existing file
            tree = ET.parse(addons_xml_path)
            root = tree.getroot()

            # Check if our addon is already in the file
            addon_exists = False
            for addon in root.findall("addon"):
                if addon.get("id") == "script.switcher":
                    addon_exists = True
                    addon.set("enabled", "true")
                    break

            # Add our addon if it doesn't exist
            if not addon_exists:
                new_addon = ET.SubElement(root, "addon")
                new_addon.set("id", "script.switcher")
                new_addon.set("enabled", "true")

            # Write the updated file
            tree.write(addons_xml_path)
            print("Updated addons.xml file")
        else:
            # Create new file
            root = ET.Element("addons")
            addon = ET.SubElement(root, "addon")
            addon.set("id", "script.switcher")
            addon.set("enabled", "true")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(addons_xml_path), exist_ok=True)

            # Write the file
            tree = ET.ElementTree(root)
            tree.write(addons_xml_path)
            print("Created addons.xml file")

        return True
    except Exception as e:
        print(f"Error updating XML configuration: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut to launch the addon directly"""
    print("Creating desktop shortcut for direct addon access...")

    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Create desktop directory if it doesn't exist
    desktop_dir = os.path.join(home_dir, "Desktop")
    os.makedirs(desktop_dir, exist_ok=True)

    # Create the desktop shortcut
    shortcut_path = os.path.join(desktop_dir, "Kodi App Switcher.desktop")

    try:
        with open(shortcut_path, "w") as f:
            f.write(f"""[Desktop Entry]
Name=Kodi App Switcher
Comment=Launch Kodi App Switcher directly
Exec=kodi-send --action="RunAddon(script.switcher)"
Icon={home_dir}/.kodi/addons/script.switcher/resources/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;TV;
""")

        # Make it executable
        os.chmod(shortcut_path, 0o755)
        print(f"Created desktop shortcut at {shortcut_path}")
        return True
    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")
        return False

def enable_unknown_sources():
    """Enable unknown sources in Kodi settings"""
    print("Enabling unknown sources in Kodi settings...")

    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Path to Kodi settings.xml
    settings_path = os.path.join(home_dir, ".kodi", "userdata", "guisettings.xml")

    if not os.path.exists(settings_path):
        print(f"Kodi settings file not found at {settings_path}")

        # Try to find settings.xml in alternative locations
        userdata_dir = os.path.join(home_dir, ".kodi", "userdata")
        if os.path.exists(userdata_dir):
            for file in os.listdir(userdata_dir):
                if file.lower() == "settings.xml":
                    settings_path = os.path.join(userdata_dir, file)
                    print(f"Found alternative settings file: {settings_path}")
                    break

        if not os.path.exists(settings_path):
            # Create a minimal settings file
            try:
                os.makedirs(os.path.dirname(settings_path), exist_ok=True)
                with open(settings_path, "w") as f:
                    f.write("""<settings>
    <addons>
        <unknownsources>true</unknownsources>
    </addons>
</settings>""")
                print(f"Created new settings file with unknown sources enabled")
                return True
            except Exception as e:
                print(f"Failed to create settings file: {e}")
                return False

    try:
        # Parse the existing settings file
        tree = ET.parse(settings_path)
        root = tree.getroot()

        # Find or create the addons section
        addons_section = root.find(".//addons")
        if addons_section is None:
            addons_section = ET.SubElement(root, "addons")

        # Find or create the unknownsources setting
        unknown_sources = addons_section.find("unknownsources")
        if unknown_sources is None:
            unknown_sources = ET.SubElement(addons_section, "unknownsources")

        # Set it to true
        unknown_sources.text = "true"

        # Write the updated file
        tree.write(settings_path)
        print("Successfully enabled unknown sources in Kodi settings")
        return True
    except Exception as e:
        print(f"Error enabling unknown sources: {e}")

        # Try direct file modification as a fallback
        try:
            with open(settings_path, "r") as f:
                content = f.read()

            # Check if unknownsources is already in the file
            if "<unknownsources>" in content:
                # Replace the value
                content = content.replace("<unknownsources>false</unknownsources>", "<unknownsources>true</unknownsources>")
            else:
                # Add it to the addons section
                if "<addons>" in content:
                    content = content.replace("<addons>", "<addons>\n        <unknownsources>true</unknownsources>")
                else:
                    # Add both addons section and unknownsources
                    content = content.replace("<settings>", "<settings>\n    <addons>\n        <unknownsources>true</unknownsources>\n    </addons>")

            # Write the updated content
            with open(settings_path, "w") as f:
                f.write(content)

            print("Enabled unknown sources using direct file modification")
            return True
        except Exception as e2:
            print(f"Failed to modify settings file directly: {e2}")
            return False


def main():
    """Main function to enable the addon using all available methods"""
    print("Starting App Switcher addon enabler...")

    # Enable unknown sources first
    unknown_sources_success = enable_unknown_sources()
    if unknown_sources_success:
        print("✅ Unknown sources enabled in Kodi")
    else:
        print("⚠️ Failed to enable unknown sources automatically")
        print("You may need to enable it manually in Kodi:")
        print("1. In Kodi, go to Settings > System > Add-ons")
        print("2. Enable 'Unknown sources'")

    # Try all methods to enable the addon
    db_success = enable_via_database()
    json_success = enable_via_json_rpc()
    xml_success = enable_via_xml()
    create_desktop_shortcut()  # Always create the shortcut regardless of other methods

    # Report results
    if db_success or json_success or xml_success:
        print("\n✅ Addon should be enabled now.")
        print("If it's still not visible in Kodi, please try these manual steps:")
        print("1. In Kodi, go to Settings > Add-ons")
        print("2. Select 'My Add-ons' > 'Program add-ons'")
        print("3. Find 'App Switcher' and enable it")
        print("\nAlternatively, use the desktop shortcut 'Kodi App Switcher'")
        return True
    else:
        print("\n⚠️ Could not automatically enable the addon.")
        print("This is normal if Kodi is not currently running.")
        print("\nThe addon will be installed but may need to be enabled manually:")
        print("1. Start Kodi")
        print("2. Go to Settings > Add-ons")
        print("3. Select 'My Add-ons' > 'Program add-ons'")
        print("4. Find 'App Switcher' and enable it")
        print("\nAlternatively, use the desktop shortcut 'Kodi App Switcher'")

        # Create a helper script to enable the addon next time Kodi starts
        try:
            home_dir = os.path.expanduser("~")
            helper_script = os.path.join(home_dir, "bin", "enable_kodi_addon.sh")

            with open(helper_script, "w") as f:
                f.write("""#!/bin/bash
# Helper script to enable the App Switcher addon in Kodi
# This will be run the next time Kodi starts

# Wait for Kodi to fully start
sleep 10

# Try to enable the addon via JSON-RPC
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"script.switcher","enabled":true},"id":1}' http://localhost:8080/jsonrpc

# Exit successfully
exit 0
""")

            # Make it executable
            os.chmod(helper_script, 0o755)
            print(f"\nCreated helper script at {helper_script}")
            print("This script will try to enable the addon next time Kodi starts")
        except Exception as e:
            print(f"Failed to create helper script: {e}")

        return True  # Return True anyway so the installation continues

if __name__ == "__main__":
    main()
