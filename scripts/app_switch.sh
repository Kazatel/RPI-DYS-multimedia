#!/bin/bash
# App switching script that uses the service_manager.py wrapper

# Get the project directory path
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$PROJECT_DIR/scripts"

# Path to the service_manager.py script
SERVICE_MANAGER="$SCRIPT_DIR/service_manager.py"

# Check if the app parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <kodi|retropie|emulationstation|desktop>"
  exit 1
fi

# Map the input parameter to the correct service name
APP="$1"
SERVICE=""

case "$APP" in
  kodi)
    SERVICE="kodi"
    ;;
  retropie|emulationstation)
    SERVICE="emulationstation"
    ;;
  desktop)
    SERVICE="desktop"
    ;;
  *)
    echo "Unknown app: $APP"
    echo "Usage: $0 <kodi|retropie|emulationstation|desktop>"
    exit 1
    ;;
esac

# Check if the service manager script exists
if [ ! -f "$SERVICE_MANAGER" ]; then
  echo "Error: Service manager script not found at $SERVICE_MANAGER"
  exit 1
fi

# Make sure the script is executable
chmod +x "$SERVICE_MANAGER"

# Use the service manager to switch to the requested application
echo "Switching to $SERVICE using service manager..."
python3 "$SERVICE_MANAGER" switch "$SERVICE"

# Check the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "Successfully switched to $SERVICE"
else
  echo "Failed to switch to $SERVICE (exit code $EXIT_CODE)"
fi

exit $EXIT_CODE