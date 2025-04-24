#!/usr/bin/env python3
"""
App Switcher Addon for Kodi
Allows switching between Kodi, RetroPie, and Desktop Environment
"""

import os
import subprocess
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

# Get addon info
ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

# Define the applications and their services
APPLICATIONS = {
    "retropie": {
        "name": "RetroPie",
        "service": "retropie.service",
        "icon": os.path.join(ADDON_PATH, "resources", "retropie.png")
    },
    "desktop": {
        "name": "Desktop Environment",
        "service": "desktop.service",
        "icon": os.path.join(ADDON_PATH, "resources", "desktop.png")
    }
}

class AppSwitcherDialog(xbmcgui.Dialog):
    """Dialog for switching between applications"""
    
    def __init__(self):
        super(AppSwitcherDialog, self).__init__()
        
    def show_menu(self):
        """Show the app switcher menu"""
        # Create list of options
        options = []
        for app_id, app_info in APPLICATIONS.items():
            options.append(app_info["name"])
        
        # Show dialog
        index = self.select("Switch to Application", options)
        
        # Handle selection
        if index >= 0:
            app_id = list(APPLICATIONS.keys())[index]
            self.switch_to_app(app_id)
    
    def switch_to_app(self, app_id):
        """Switch to the selected application"""
        if app_id not in APPLICATIONS:
            self.notification(ADDON_NAME, f"Unknown application: {app_id}", xbmcgui.NOTIFICATION_ERROR)
            return
        
        app_info = APPLICATIONS[app_id]
        service_name = app_info["service"]
        
        # Confirm switch
        if not self.yesno(ADDON_NAME, f"Switch to {app_info['name']}?"):
            return
        
        # Execute the switch
        try:
            # Use systemctl to start the service
            xbmc.executebuiltin(f"Notification({ADDON_NAME}, Switching to {app_info['name']}...)")
            xbmc.sleep(2000)  # Give time for notification to show
            
            # Use subprocess to start the service
            # This will effectively close Kodi and start the other application
            subprocess.Popen(["sudo", "systemctl", "start", service_name])
            
        except Exception as e:
            self.notification(ADDON_NAME, f"Error switching: {str(e)}", xbmcgui.NOTIFICATION_ERROR)


def run():
    """Main entry point for the addon"""
    dialog = AppSwitcherDialog()
    dialog.show_menu()


if __name__ == "__main__":
    run()
