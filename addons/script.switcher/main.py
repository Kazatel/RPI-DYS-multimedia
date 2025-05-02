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

# Define the applications
APPLICATIONS = {
    "retropie": {
        "name": "RetroPie",
        "icon": os.path.join(ADDON_PATH, "resources", "retropie.png")
    },
    "desktop": {
        "name": "Desktop Environment",
        "icon": os.path.join(ADDON_PATH, "resources", "desktop.png")
    }
}

# Try to find icons in user's Pictures/icons directory
home_dir = os.path.expanduser("~")
icons_dir = os.path.join(home_dir, "Pictures", "icons")
if os.path.exists(icons_dir):
    for app_id in APPLICATIONS:
        user_icon = os.path.join(icons_dir, f"{app_id}.png")
        if os.path.exists(user_icon):
            APPLICATIONS[app_id]["icon"] = user_icon

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

        # Confirm switch
        if not self.yesno(ADDON_NAME, f"Switch to {app_info['name']}?"):
            return

        # Execute the switch
        try:
            # Show notification
            xbmc.executebuiltin(f"Notification({ADDON_NAME}, Switching to {app_info['name']}...)")
            xbmc.sleep(2000)  # Give time for notification to show

            # Use app_switch.sh script from the user's bin directory
            # This will effectively close Kodi and start the other application
            app_switch_path = os.path.expanduser("~/bin/app_switch.sh")

            # Check if the script exists
            if not os.path.exists(app_switch_path):
                self.notification(ADDON_NAME, f"app_switch.sh not found at {app_switch_path}", xbmcgui.NOTIFICATION_ERROR)
                return

            # Make sure it's executable
            if not os.access(app_switch_path, os.X_OK):
                try:
                    os.chmod(app_switch_path, 0o755)
                except Exception:
                    self.notification(ADDON_NAME, f"Could not make {app_switch_path} executable", xbmcgui.NOTIFICATION_ERROR)
                    return

            # Launch the script
            subprocess.Popen([app_switch_path, app_id])

        except Exception as e:
            self.notification(ADDON_NAME, f"Error switching: {str(e)}", xbmcgui.NOTIFICATION_ERROR)


def run():
    """Main entry point for the addon"""
    dialog = AppSwitcherDialog()
    dialog.show_menu()


if __name__ == "__main__":
    run()
