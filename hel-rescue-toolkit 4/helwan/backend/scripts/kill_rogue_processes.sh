#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Detecting and offering to kill rogue processes (top 5 by CPU/RAM usage)..."
echo "WARNING: Killing system processes can lead to instability or data loss. Use with extreme caution!" >&2

# Get top 5 processes by CPU usage (excluding system processes like kworker, systemd, etc.)
echo "Top 5 processes by CPU usage:"
ps aux --sort=-%cpu | awk 'NR>1 {print $1, $2, $3, $11}' | head -n 5 | column -t

# Get top 5 processes by Memory usage
echo ""
echo "Top 5 processes by Memory usage:"
ps aux --sort=-%mem | awk 'NR>1 {print $1, $2, $4, $11}' | head -n 5 | column -t

echo ""
echo "To kill a process, please provide its PID (Process ID) or type 'cancel':"
read -r PID_TO_KILL

if [ -z "$PID_TO_KILL" ] || [ "$PID_TO_KILL" = "cancel" ]; then
    echo "Operation cancelled."
    exit 0
fi

# Basic validation for PID
if ! [[ "$PID_TO_KILL" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid PID provided. Please enter a numeric PID." >&2
    exit 1
fi

# Check if process exists
if ! ps -p "$PID_TO_KILL" > /dev/null; then
    echo "Error: Process with PID '$PID_TO_KILL' does not exist." >&2
    exit 1
fi

echo "Attempting to kill process with PID: $PID_TO_KILL"
kill -9 "$PID_TO_KILL" # Use kill -9 for forceful termination

if [ $? -eq 0 ]; then
  echo "✅ Process with PID '$PID_TO_KILL' killed successfully."
  exit 0
else
  echo "❌ Failed to kill process with PID '$PID_TO_KILL'. Check permissions or if process is unkillable." >&2
  exit 1
fi