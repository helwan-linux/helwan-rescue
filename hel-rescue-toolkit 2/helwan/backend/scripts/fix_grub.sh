#!/bin/bash

# Dependency check function
check_dependency() {
  command -v "$1" >/dev/null 2>&1 || { echo >&2 "Error: Required command '$1' is not installed. Aborting."; exit 1; }
}

if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Please run this tool as root!"
  exit 1
fi

# Check for required commands
check_dependency "grub-install"
check_dependency "grub-mkconfig"
check_dependency "ls" # For /boot detection
check_dependency "grep"
check_dependency "sed"

echo "📌 Detecting EFI system..."
efidir="/boot/efi"

if [ ! -d "$efidir" ]; then
  echo "❌ EFI directory not found at $efidir. This script requires an EFI system."
  exit 1
fi

echo "🔧 Reinstalling GRUB..."
grub-install --target=x86_64-efi --efi-directory="$efidir" --bootloader-id=GRUB --recheck
if [ $? -ne 0 ]; then
    echo "❌ GRUB installation failed. Please check output above."
    exit 1
fi

echo "🔄 Regenerating GRUB config..."
grub-mkconfig -o /boot/grub/grub.cfg
if [ $? -ne 0 ]; then
    echo "❌ GRUB configuration generation failed. Please check output above."
    exit 1
fi

echo "✅ GRUB restored successfully."
