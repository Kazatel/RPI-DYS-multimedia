#!/bin/bash
# App switching script that uses systemd services

APP="$1"

if [ -z "$APP" ]; then
  echo "Usage: $0 <kodi|retropie|desktop>"
  exit 1
fi

# Function to check if a service is active
is_service_active() {
  systemctl --user is-active "$1.service" >/dev/null 2>&1
}

# Function to start a service
start_service() {
  echo "Starting $1..."
  systemctl --user start "$1.service"
}

# Function to stop a service
stop_service() {
  echo "Stopping $1..."
  systemctl --user stop "$1.service"
}

# Stop any running services
for service in kodi retropie desktop; do
  if is_service_active "$service"; then
    stop_service "$service"
  fi
done

# Start the requested service
case "$APP" in
  kodi)
    start_service "kodi"
    ;;
  retropie|emulationstation)
    start_service "retropie"
    ;;
  desktop)
    start_service "desktop"
    ;;
  *)
    echo "Unknown app: $APP"
    echo "Usage: $0 <kodi|retropie|desktop>"
    exit 1
    ;;
esac

exit 0
