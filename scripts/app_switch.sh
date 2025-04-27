#!/bin/bash

NEXT_APP="$1"

if [ -z "$NEXT_APP" ]; then
  echo "Usage: $0 <kodi|emulationstation|desktop>"
  exit 1
fi

graceful_exit() {
  local process_name="$1"

  if pgrep -x "$process_name" >/dev/null; then
    echo "Closing $process_name..."
    pkill "$process_name"
    sleep 3

    local timeout=10
    while pgrep -x "$process_name" >/dev/null && [ $timeout -gt 0 ]; do
      echo "Waiting for $process_name to exit..."
      sleep 1
      timeout=$((timeout-1))
    done

    if pgrep -x "$process_name" >/dev/null; then
      echo "$process_name did not exit gracefully, force killing..."
      pkill -9 "$process_name"
      sleep 2
    fi

    echo "$process_name closed."
  fi
}

# Always close these apps if they are running
graceful_exit "kodi.bin"
graceful_exit "emulationstation"
graceful_exit "lxsession"

# Now start the next app
echo "Starting $NEXT_APP..."

case "$NEXT_APP" in
  kodi)
    kodi &
    ;;
  emulationstation|retropie)
    emulationstation &
    ;;
  desktop)
    startlxsession &
    ;;
  *)
    echo "Unknown app: $NEXT_APP"
    echo "Usage: $0 <kodi|retropie|emulationstation|desktop>"
    exit 1
    ;;
esac
