#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

echo "📌 Detecting EFI system..."
efidir="/boot/efi"

if [ ! -d "$efidir" ]; then
  echo "❌ EFI directory not found at $efidir"
  exit 1
fi

echo "🔧 Reinstalling GRUB..."
grub-install --target=x86_64-efi --efi-directory="$efidir" --bootloader-id=GRUB --recheck

echo "🔄 Regenerating GRUB config..."
grub-mkconfig -o /boot/grub/grub.cfg

echo "✅ GRUB restored successfully."
