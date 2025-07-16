#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Checking recent system journal logs (last 50 lines by default)..."
echo "  • To view boot logs, type 'boot'."
echo "  • To view logs for a specific service, type 'service <service_name>'."
echo "  • To view all logs, type 'all'."
echo "  • To view logs from previous boot, add '-b -1'."
echo "  • Type 'cancel' to exit."
echo ""
echo "Enter command (e.g., 'boot', 'service systemd-udevd', 'all', or 'cancel'):"
read -r JOURNAL_CMD

case "$JOURNAL_CMD" in
    "boot")
        echo "Displaying boot messages:"
        journalctl -b -p err..warn -n 50 --no-pager
        ;;
    "all")
        echo "Displaying all recent journal logs (last 50 lines):"
        journalctl -n 50 --no-pager
        ;;
    "service "*)
        SERVICE_NAME=$(echo "$JOURNAL_CMD" | cut -d' ' -f2-)
        if [ -z "$SERVICE_NAME" ]; then
            echo "Error: Service name not provided. Usage: 'service <service_name>'" >&2
            exit 1
        fi
        echo "Displaying logs for service: $SERVICE_NAME (last 50 lines):"
        journalctl -u "$SERVICE_NAME" -n 50 --no-pager
        ;;
    "cancel")
        echo "Operation cancelled."
        exit 0
        ;;
    *)
        echo "Displaying last 50 lines of journal logs by default (invalid command or no input):"
        journalctl -n 50 --no-pager
        ;;
esac

if [ $? -eq 0 ]; then
  echo "✅ Journal log check complete."
  exit 0
else
  echo "❌ Failed to retrieve journal logs. Check 'journalctl' utility or permissions." >&2
  exit 1
fi