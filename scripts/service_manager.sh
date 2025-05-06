#!/bin/bash
# Versatile service management script for killing and starting applications

# Make sure this script runs as bash, not sh
if [ -z "$BASH_VERSION" ]; then
  echo "This script must be run with bash, not sh"
  exec bash "$0" "$@"
fi

# Check parameters
ACTION="$1"
SERVICE="$2"

# Validate input
if [ -z "$ACTION" ] || [ -z "$SERVICE" ]; then
  echo "Usage: $0 <kill|start> <kodi|emulationstation|desktop>"
  exit 1
fi

# Our own PID and the PID of our parent process - we'll make sure not to kill these
OUR_PID=$$
PARENT_PID=$PPID
echo "Script running as PID $OUR_PID with parent PID $PARENT_PID"

# Enhanced function to kill processes by name
terminate_app() {
  local app_name="$1"
  local is_pattern="$2"  # true/false - whether to use -f with pgrep
  local pids
 
  echo "Looking for '$app_name' processes..."
 
  # Get all matching PIDs
  if [ "$is_pattern" = "true" ]; then
    pids=$(pgrep -f "$app_name" 2>/dev/null)
  else
    pids=$(pgrep "$app_name" 2>/dev/null)
  fi
 
  # If no processes found, return early
  if [ -z "$pids" ]; then
    echo "No processes found matching '$app_name'"
    return
  fi
 
  echo "Found processes matching '$app_name': $pids"
 
  # First, try graceful termination
  for pid in $pids; do
    # Skip our own PID and parent PID
    if [ "$pid" != "$OUR_PID" ] && [ "$pid" != "$PARENT_PID" ]; then
      echo "Sending TERM signal to PID $pid"
      kill -15 "$pid" 2>/dev/null
    else
      echo "Skipping PID $pid (it's our script or parent)"
    fi
  done
 
  # Wait a bit for processes to exit gracefully
  sleep 2
 
  # Check if processes are still running and force kill if necessary
  if [ "$is_pattern" = "true" ]; then
    pids=$(pgrep -f "$app_name" 2>/dev/null)
  else
    pids=$(pgrep "$app_name" 2>/dev/null)
  fi
 
  if [ -n "$pids" ]; then
    echo "Some processes still running, force killing: $pids"
    for pid in $pids; do
      if [ "$pid" != "$OUR_PID" ] && [ "$pid" != "$PARENT_PID" ]; then
        echo "Sending KILL signal to PID $pid"
        kill -9 "$pid" 2>/dev/null
      fi
    done
  fi
  
  # Final verification
  sleep 1
  if [ "$is_pattern" = "true" ]; then
    pids=$(pgrep -f "$app_name" 2>/dev/null)
  else
    pids=$(pgrep "$app_name" 2>/dev/null)
  fi
  
  if [ -n "$pids" ]; then
    echo "WARNING: Some processes still running: $pids"
    echo "These may need to be terminated manually"
  else
    echo "All '$app_name' processes successfully terminated"
  fi
}

# Function to start an application
start_app() {
  local app_name="$1"
  
  echo "Starting $app_name..."
  
  case "$app_name" in
    kodi)
      kodi >/dev/null 2>&1 &
      ;;
    emulationstation)
      nohup emulationstation >/dev/null 2>&1 &
      if [ -n "$BASH_VERSION" ]; then
        disown
      fi
      ;;
    desktop)
      # Check if we're already in X session
      if [ -n "$DISPLAY" ]; then
        echo "Already in X session, starting LXDE directly"
        lxsession -s LXDE-pi -e LXDE &
      else
        echo "Starting X session"
        startx &
      fi
      ;;
    *)
      echo "Unknown app: $app_name"
      exit 1
      ;;
  esac
  
  # Check if app launched successfully
  sleep 2
  case "$app_name" in
    kodi)
      if pgrep kodi >/dev/null || pgrep kodi.bin >/dev/null; then
        echo "Kodi has been launched successfully"
      else
        echo "WARNING: Kodi may not have launched properly"
      fi
      ;;
    emulationstation)
      if pgrep -f emulationstation >/dev/null; then
        echo "EmulationStation has been launched successfully"
      else
        echo "WARNING: EmulationStation may not have launched properly"
      fi
      ;;
    desktop)
      if pgrep lxsession >/dev/null; then
        echo "LXDE session has been launched successfully"
      else
        echo "WARNING: LXDE session may not have launched properly"
      fi
      ;;
  esac
}

# Main script logic
if [ "$ACTION" = "kill" ]; then
  echo "=== Terminating $SERVICE ==="
  
  case "$SERVICE" in
    kodi)
      terminate_app "kodi" "false"
      terminate_app "kodi.bin" "false"
      ;;
    emulationstation)
      terminate_app "emulationstation" "true"
      ;;
    desktop)
      terminate_app "lxsession" "true"
      ;;
    *)
      echo "Unknown service: $SERVICE"
      echo "Usage: $0 <kill|start> <kodi|emulationstation|desktop>"
      exit 1
      ;;
  esac
  
elif [ "$ACTION" = "start" ]; then
  echo "=== Starting $SERVICE ==="
  start_app "$SERVICE"
  
else
  echo "Unknown action: $ACTION"
  echo "Usage: $0 <kill|start> <kodi|emulationstation|desktop>"
  exit 1
fi

exit 0