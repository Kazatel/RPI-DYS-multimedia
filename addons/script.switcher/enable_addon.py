#!/usr/bin/env python3
"""
Script to enable the App Switcher addon in Kodi
"""

import os
import sqlite3
import sys
import json

def enable_addon():
    """Enable the App Switcher addon in Kodi's database"""
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    
    # Kodi database path
    addons_db_path = os.path.join(home_dir, ".kodi", "userdata", "Database", "Addons33.db")
    
    # Check if the database exists
    if not os.path.exists(addons_db_path):
        print(f"Kodi addons database not found at {addons_db_path}")
        
        # Try to find any Addons database
        userdata_dir = os.path.join(home_dir, ".kodi", "userdata", "Database")
        if os.path.exists(userdata_dir):
            for file in os.listdir(userdata_dir):
                if file.startswith("Addons") and file.endswith(".db"):
                    addons_db_path = os.path.join(userdata_dir, file)
                    print(f"Found alternative database: {addons_db_path}")
                    break
        
        if not os.path.exists(addons_db_path):
            print("No Kodi addons database found. The addon will need to be enabled manually.")
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
        
        # Create addon_data directory and settings file
        addon_data_dir = os.path.join(home_dir, ".kodi", "userdata", "addon_data", "script.switcher")
        os.makedirs(addon_data_dir, exist_ok=True)
        
        # Create settings.xml
        settings_path = os.path.join(addon_data_dir, "settings.xml")
        with open(settings_path, "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n</settings>')
        
        print("Created addon data directory and settings file")
        return True
    except Exception as e:
        print(f"Error enabling addon: {e}")
        return False

if __name__ == "__main__":
    enable_addon()
