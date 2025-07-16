#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to regenerate initramfs..."

# Find all installed kernels
KERNELS=$(ls /boot/vmlinuz-* 2>/dev/null | sed 's/.*vmlinuz-//')

if [ -z "$KERNELS" ]; then
  echo "Error: No kernel files found in /boot." >&2
  echo "Please ensure your kernel is installed correctly." >&2
  exit 1
fi

echo "Detected kernels: $KERNELS"

# Regenerate initramfs for all detected kernels
# mkinitcpio -P automatically handles all kernels defined in mkinitcpio.d
echo "  • Running mkinitcpio -P to regenerate all initramfs images..."
mkinitcpio -P

if [ $? -eq 0 ]; then
  echo "✅ Initramfs regenerated successfully for all kernels."
  exit 0
else
  echo "❌ Failed to regenerate initramfs. Please check mkinitcpio logs for errors." >&2
  exit 1
fi