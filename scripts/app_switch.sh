#!/bin/bash
# Simple app switching script that works without root privileges

APP="$1"

# Kill current app processes (using pkill -u to only kill user's processes)
pkill -u $USER -f kodi
pkill -u $USER -f emulationstation
pkill -u $USER -f lxsession

# Wait for processes to terminate
sleep 2

case "$APP" in
  kodi)
    nohup kodi > /dev/null 2>&1 & ;;
  retropie)
    nohup emulationstation > /dev/null 2>&1 & ;;
  desktop)
    nohup startx > /dev/null 2>&1 & ;;
  *)
    echo "Usage: app_switch.sh [kodi|retropie|desktop]"
    exit 1 ;;
esac

# Exit successfully
exit 0
