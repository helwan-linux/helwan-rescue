#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to backup home directories to a USB device..."

# Find a mounted USB device
USB_MOUNT_POINT=$(lsblk -o MOUNTPOINT,TYPE,TRAN | grep 'usb' | grep 'part' | awk '{print $1}' | head -n 1)

if [ -z "$USB_MOUNT_POINT" ]; then
    echo "Error: No mounted USB device found. Please ensure a USB drive is connected and mounted." >&2
    exit 1
fi

BACKUP_FILENAME="home_backup_$(date +%Y-%m-%d_%H-%M-%S).tar.gz"
BACKUP_PATH="$USB_MOUNT_POINT/$BACKUP_FILENAME"

echo "  • Found USB device mounted at: $USB_MOUNT_POINT"
echo "  • Creating backup archive: $BACKUP_PATH"

# Create a compressed tar archive of /home
tar -czf "$BACKUP_PATH" /home

if [ $? -eq 0 ]; then
  echo "✅ Home directories backed up successfully to '$BACKUP_PATH'."
  exit 0
else
  echo "❌ Failed to create home directory backup. Check disk space on USB or permissions." >&2
  exit 1
fi