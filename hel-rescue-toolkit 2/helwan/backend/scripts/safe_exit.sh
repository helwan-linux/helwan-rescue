#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to safely unmount the installed system..."

# Unmount bind mounts in reverse order
for dir in run sys proc dev; do
    if mountpoint -q "/mnt/$dir"; then
        echo "  • Unmounting /mnt/$dir..."
        umount -R "/mnt/$dir" 2>/dev/null
    fi
done

# Unmount EFI partition if it was mounted by us
if mountpoint -q /mnt/boot/efi; then
    echo "  • Unmounting /mnt/boot/efi..."
    umount /mnt/boot/efi 2>/dev/null
fi

# Finally, unmount the root partition
if mountpoint -q /mnt; then
    echo "  • Unmounting /mnt..."
    umount /mnt 2>/dev/null
fi

if mountpoint -q /mnt; then
  echo "❌ Failed to unmount all partitions. Some directories might still be mounted in /mnt." >&2
  echo "   - Please check manually and unmount if necessary." >&2
  exit 1
else
  echo "✅ All system partitions unmounted safely."
  exit 0
fi