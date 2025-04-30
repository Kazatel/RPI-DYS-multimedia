#!/bin/bash
# ^^ Important: Make sure to use #!/bin/bash NOT #!/bin/sh

NEXT_APP="$1"
if [ -z "$NEXT_APP" ]; then
  echo "Usage: $0 <kodi|emulationstation|desktop>"
  exit 1
fi

# Function to get a process and all its child processes (in reverse order)
getfamilypids() {
    local inpid="$1"
    local pidarray=""

    getfamilypidshelper() {
        local pidin="$1"
        pidarray="$pidarray $pidin"
        local CPIDS=$(pgrep -P "$pidin")
        for cpid in $CPIDS; do
            getfamilypidshelper "$cpid"
        done
    }

    getfamilypidshelper "$inpid"

    # Reverse the order (children before parents)
    local reversed_pids=""
    for pid in $pidarray; do
        reversed_pids="$pid $reversed_pids"
    done

    echo "$reversed_pids"
}

graceful_exit() {
  local process_name="$1"
  
  # Find the main process PID(s)
  local main_pids=$(pgrep -x "$process_name")
  
  if [ -n "$main_pids" ]; then
    echo "Closing $process_name..."
    
    for pid in $main_pids; do
      echo "Processing main process $process_name (PID: $pid) and its children..."
      
      # Get all child PIDs in proper order (children before parents)
      local family_pids=$(getfamilypids "$pid")
      
      # Count family members
      local count=0
      for fpid in $family_pids; do
        count=$((count + 1))
      done
      
      if [ $count -gt 1 ]; then
        echo "Found $count processes in the family tree"
      fi
      
      # First try graceful termination of all processes
      for fpid in $family_pids; do
        kill -15 "$fpid" 2>/dev/null
      done
      
      # Wait up to 10 seconds for processes to exit
      local timeout=10
      while [ $timeout -gt 0 ]; do
        local all_exited=true
        for fpid in $family_pids; do
          if kill -0 "$fpid" 2>/dev/null; then
            all_exited=false
            break
          fi
        done
        
        if $all_exited; then
          echo "All processes exited gracefully."
          break
        fi
        
        echo "Waiting for processes to exit... ($timeout seconds left)"
        sleep 1
        timeout=$((timeout-1))
      done
      
      # Force kill any remaining processes
      for fpid in $family_pids; do
        if kill -0 "$fpid" 2>/dev/null; then
          echo "Force killing PID $fpid..."
          kill -9 "$fpid" 2>/dev/null
        fi
      done
    done
    
    echo "$process_name and all child processes closed."
  fi
}

# Handle Kodi - the getfamilypids function will find all child processes automatically
graceful_exit "kodi"
graceful_exit "emulationstation"
graceful_exit "lxsession"

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
    startx &
    ;;
  *)
    echo "Unknown app: $NEXT_APP"
    exit 1
    ;;
esac