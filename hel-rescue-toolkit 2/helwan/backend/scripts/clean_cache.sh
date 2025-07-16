#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

echo "🧹 Cleaning pacman cache..."
yes | pacman -Scc

echo "🗑 Removing logs older than 7 days..."
find /var/log -type f -mtime +7 -exec rm -f {} \;

echo "✅ System cleaned."
