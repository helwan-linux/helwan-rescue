#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Run this as root."
  exit 1
fi

log_archive="/tmp/helwan_logs_$(date +%F_%H%M).tar.gz"

echo "Collecting logs..."
tar -czf "$log_archive" /var/log

echo "Searching for USB devices..."
usb_mount=$(lsblk -o MOUNTPOINT,TRAN | grep usb | awk '{print $1}' | head -n1)

if [ -z "$usb_mount" ]; then
  echo "No mounted USB device found."
  echo "Logs saved locally at: $log_archive"
  exit 0
fi

cp "$log_archive" "$usb_mount/"

echo "Logs exported to $usb_mount"
