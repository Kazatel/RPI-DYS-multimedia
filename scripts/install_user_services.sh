#!/bin/bash
# Script to install user services for app switching

# Get the username
USERNAME=$(whoami)
if [ "$USERNAME" = "root" ]; then
  echo "This script should not be run as root."
  echo "Please run it as the user who will use the services."
  exit 1
fi

# Create user systemd directory if it doesn't exist
mkdir -p ~/.config/systemd/user/

# Copy service files
echo "Installing user services..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICES_DIR="$PROJECT_DIR/services"

# Replace username in service files and copy them
for service in kodi retropie desktop; do
  service_file="$SERVICES_DIR/$service.service"
  if [ -f "$service_file" ]; then
    # Replace the username in the service file
    sed "s/User=tomas/User=$USERNAME/g; s/Group=tomas/Group=$USERNAME/g" "$service_file" > ~/.config/systemd/user/$service.service
    echo "Installed $service.service for user $USERNAME"
  else
    echo "Service file $service_file not found"
  fi
done

# Reload user systemd
systemctl --user daemon-reload

echo "User services installed successfully."
echo "You can now use app_switch.sh to switch between applications."
echo ""
echo "To enable a service to start at boot:"
echo "  systemctl --user enable kodi.service"
echo "  systemctl --user enable retropie.service"
echo "  systemctl --user enable desktop.service"
echo ""
echo "To start a service manually:"
echo "  systemctl --user start kodi.service"
echo ""
echo "To check service status:"
echo "  systemctl --user status kodi.service"

exit 0
