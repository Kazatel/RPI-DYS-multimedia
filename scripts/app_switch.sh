#!/bin/bash

NEXT_APP="$1"

if [ -z "$NEXT_APP" ]; then
  echo "Usage: $0 <kodi|emulationstation|desktop>"
  exit 1
fi

graceful_exit() {
  local process_name="$1"
  local quit_command="$2"

  if pgrep -x "$process_name" >/dev/null; then
    echo "Closing $process_name..."
    
    # If there's a quit command, run it
    if [ -n "$quit_command" ]; then
      eval "$quit_command"
      sleep 3  # Give it time to start quitting
    fi

    # Wait until the process is really gone
    while pgrep -x "$process_name" >/dev/null; do
      echo "Waiting for $process_name to exit..."
      sleep 1
    done

    echo "$process_name closed."
  fi
}

# Close Kodi if running
graceful_exit "kodi" "kodi-send --action='Quit'"

# Close EmulationStation if running
graceful_exit "emulationstation" "pkill emulationstation"

# Close Desktop (LXSession or similar) if running
graceful_exit "lxsession" "pkill lxsession"

# Now start the next app
echo "Starting $NEXT_APP..."

case "$NEXT_APP" in
  kodi)
    kodi &
    ;;
  emulationstation)
    emulationstation &
    ;;
  desktop)
    startlxsession &
    ;;
  *)
    echo "Unknown app: $NEXT_APP"
    exit 1
    ;;
esac
