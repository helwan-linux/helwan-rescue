#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to fix network connectivity..."

echo "  • Restarting NetworkManager service..."
systemctl restart NetworkManager 2>/dev/null

# Check if NetworkManager restart was successful
if [ $? -ne 0 ]; then
    echo "Warning: Could not restart NetworkManager. It might not be installed or enabled." >&2
    echo "  • Attempting to bring up network interfaces using dhcpcd..."
    # Fallback to dhcpcd if NetworkManager fails
    ip link set eth0 up 2>/dev/null # Assuming eth0, may need to generalize or iterate
    dhcpcd -B 2>/dev/null
fi


echo "  • Resetting DNS resolver to 1.1.1.1..."
echo "nameserver 1.1.1.1" > /etc/resolv.conf

echo "  • Testing internet connection (ping archlinux.org)..."
ping -c 3 archlinux.org > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "✅ Network is now working correctly."
  exit 0
else
  echo "❌ Network restart complete, but no stable connection detected." >&2
  echo "   - Please check your physical connection or network configuration." >&2
  exit 1
fi