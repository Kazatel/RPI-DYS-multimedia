#!/bin/bash
# Simple app switching script

# Check if we're running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

APP="$1"
USER="tomas"  # Hardcoded user from config

# Kill current app processes
pkill -f kodi
pkill -f emulationstation
pkill -f lxsession

# Wait for processes to terminate
sleep 2

case "$APP" in
  kodi)
    su - $USER -c "nohup kodi > /dev/null 2>&1 &" ;;
  retropie)
    su - $USER -c "nohup emulationstation > /dev/null 2>&1 &" ;;
  desktop)
    su - $USER -c "nohup startx > /dev/null 2>&1 &" ;;
  *)
    echo "Usage: app_switch.sh [kodi|retropie|desktop]"
    exit 1 ;;
esac

# Exit successfully
exit 0
