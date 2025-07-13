#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

KERNEL=$(ls /boot | grep -E 'vmlinuz-linux.*' | head -n 1 | sed 's/vmlinuz-//')

if [ -z "$KERNEL" ]; then
  echo "❌ No kernel found in /boot"
  exit 1
fi

echo "🧱 Regenerating initramfs for $KERNEL..."
mkinitcpio -P

echo "✅ Initramfs regenerated successfully."
