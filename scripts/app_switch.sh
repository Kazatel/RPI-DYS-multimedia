#!/bin/bash
# Simple app switching script

APP="$1"

# Kill current app processes
pkill -f kodi
pkill -f emulationstation
pkill -f lxsession

# Wait for processes to terminate
sleep 2

case "$APP" in
  kodi)
    nohup kodi & ;;
  retropie)
    nohup emulationstation & ;;
  desktop)
    nohup startx & ;;
  *)
    echo "Usage: app_switch.sh [kodi|retropie|desktop]"
    exit 1 ;;
esac
