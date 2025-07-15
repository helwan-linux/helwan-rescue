#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

echo "🔁 Restarting networking service..."
systemctl restart NetworkManager

echo "🌐 Resetting DNS resolver..."
echo "nameserver 1.1.1.1" > /etc/resolv.conf

ping -c 2 archlinux.org > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "✅ Network is now working."
else
  echo "⚠️ Network restart complete, but no connection detected."
fi
