#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

echo "🔌 Unmounting system directories..."
for dir in dev proc sys run; do umount -R /mnt/$dir 2>/dev/null; done
umount /mnt 2>/dev/null

echo "✅ System unmounted safely."
