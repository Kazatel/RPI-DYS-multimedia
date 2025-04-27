#!/bin/bash
# Simple app switching script that works without root privileges

APP="$1"

# Kill current app processes (using pkill -u to only kill user's processes)
pkill -u $USER -f kodi
pkill -u $USER -f emulationstation
pkill -u $USER -f lxsession

# Wait for processes to terminate
sleep 2

# Set up environment variables
export DISPLAY=:0
export XAUTHORITY=$HOME/.Xauthority

case "$APP" in
  kodi)
    nohup /usr/bin/kodi --standalone > $HOME/kodi_output.log 2>&1 & ;;
  retropie)
    nohup /usr/bin/emulationstation > $HOME/retropie_output.log 2>&1 & ;;
  desktop)
    nohup /usr/bin/startx > $HOME/desktop_output.log 2>&1 & ;;
  *)
    echo "Usage: app_switch.sh [kodi|retropie|desktop]"
    exit 1 ;;
esac

# Exit successfully
exit 0
