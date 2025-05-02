#!/bin/bash
# App switching script that uses the service_manager.py wrapper

# Try to determine the project directory path
if [ -f "${BASH_SOURCE[0]}" ]; then
  # If this script is being run directly
  PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
else
  # Fallback to hardcoded path if script is called from somewhere else
  PROJECT_DIR="/home/tomas/rpi_dys"
fi
SCRIPT_DIR="$PROJECT_DIR/scripts"

# Paths to the service manager scripts
SERVICE_MANAGER_PY="$SCRIPT_DIR/service_manager.py"
SERVICE_MANAGER_SH="$SCRIPT_DIR/service_manager.sh"

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

# Check if the service manager scripts exist
if [ ! -f "$SERVICE_MANAGER_PY" ]; then
  echo "Error: Service manager Python script not found at $SERVICE_MANAGER_PY"
  exit 1
fi

if [ ! -f "$SERVICE_MANAGER_SH" ]; then
  echo "Error: Service manager Shell script not found at $SERVICE_MANAGER_SH"
  exit 1
fi

# Make sure the scripts are executable
chmod +x "$SERVICE_MANAGER_PY"
chmod +x "$SERVICE_MANAGER_SH"

# Use the service manager to switch to the requested application
echo "Switching to $SERVICE using service manager..."
python3 "$SERVICE_MANAGER_PY" switch "$SERVICE"

# Check the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "Successfully switched to $SERVICE"
else
  echo "Failed to switch to $SERVICE (exit code $EXIT_CODE)"
fi

exit $EXIT_CODE