#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

echo "🖥 Kernel: $(uname -r)"
echo "🧠 RAM Total: $(free -h | awk '/Mem/ {print $2}')"
echo "💽 Disk Free on /: $(df -h / | awk 'NR==2{print $4}')"

echo "🌐 Checking internet..."
if ping -c 1 archlinux.org &>/dev/null; then
  echo "✅ Online"
else
  echo "❌ Offline"
fi
