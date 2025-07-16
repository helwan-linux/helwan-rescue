#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

# Check if /mnt is already mounted. If so, unmount it first for a clean start.
if mountpoint -q /mnt; then
    echo "Warning: /mnt is already mounted. Attempting to unmount for a clean chroot setup."
    # Use safe_exit.sh logic for unmounting, but only if it's our mounts
    if mountpoint -q /mnt/dev || mountpoint -q /mnt/proc || mountpoint -q /mnt/sys || mountpoint -q /mnt/run; then
        for dir in dev proc sys run; do umount -R "/mnt/$dir" 2>/dev/null; done
    fi
    umount "/mnt" 2>/dev/null
    if mountpoint -q /mnt; then
        echo "Error: Could not unmount /mnt. Please unmount manually and try again." >&2
        exit 1
    fi
fi

echo "Detecting root partition of the installed system..."

# Use lsblk to find the root partition.
# This command tries to find the partition that *would* be mounted as /
# It searches for partitions with an Arch Linux filesystem (ext4, btrfs, xfs, f2fs)
# and which are not already mounted (to avoid picking up the live ISO's root).
# This is a heuristic and might need manual input for complex setups (e.g., LVM, RAID).
ROOT_PARTITION=$(lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINT | grep 'part' | awk '{print $1,$3,$4}' | while read -r name fstype mountpoint; do
    if [[ "$fstype" =~ ^(ext4|btrfs|xfs|f2fs)$ && "$mountpoint" == "" ]]; then
        # Check if it contains common root directories as a sanity check
        # Temporarily mount it to check, then unmount
        TMP_MOUNT_DIR=$(mktemp -d)
        if mount "/dev/$name" "$TMP_MOUNT_DIR" 2>/dev/null; then
            if [ -d "$TMP_MOUNT_DIR/etc" ] && [ -d "$TMP_MOUNT_DIR/home" ] && [ -d "$TMP_MOUNT_DIR/usr" ] && [ -d "$TMP_MOUNT_DIR/var" ]; then
                echo "/dev/$name"
                umount "$TMP_MOUNT_DIR" 2>/dev/null
                rmdir "$TMP_MOUNT_DIR"
                exit 0 # Found it, exit loop
            fi
            umount "$TMP_MOUNT_DIR" 2>/dev/null
        fi
        rmdir "$TMP_MOUNT_DIR" 2>/dev/null
    fi
done | head -n 1) # Take the first one found

# Fallback: if automatic detection fails, prompt the user for the root partition
if [ -z "$ROOT_PARTITION" ]; then
    echo "Warning: Automatic root partition detection failed. Please manually provide the root partition (e.g., /dev/sda1):"
    read -r MANUAL_PARTITION
    if [ -b "$MANUAL_PARTITION" ]; then # Check if it's a block device
        ROOT_PARTITION="$MANUAL_PARTITION"
    else
        echo "Error: Invalid or non-existent partition provided: $MANUAL_PARTITION" >&2
        exit 1
    fi
fi

echo "Selected root partition: $ROOT_PARTITION"

echo "Mounting root partition to /mnt..."
mount "$ROOT_PARTITION" /mnt

if [ $? -ne 0 ]; then
  echo "Error: Failed to mount root partition '$ROOT_PARTITION' to /mnt." >&2
  echo "Please check the partition or try mounting manually." >&2
  exit 1
fi

echo "Mounting essential directories for chroot..."
# Create mount points if they don't exist (e.g., if /mnt was empty or re-created)
mkdir -p /mnt/{dev,proc,sys,run,boot/efi} 2>/dev/null

mount --bind /dev /mnt/dev
mount --bind /proc /mnt/proc
mount --bind /sys /mnt/sys
mount --bind /run /mnt/run

# Optional: Mount EFI partition if detected
EFI_PARTITION=$(lsblk -o NAME,FSTYPE,MOUNTPOINT | grep -E 'vfat.*EFI' | awk '{print "/dev/" $1}' | head -n 1)
if [ -n "$EFI_PARTITION" ]; then
    echo "  • Detected EFI partition: $EFI_PARTITION"
    if ! mountpoint -q /mnt/boot/efi; then # Only mount if not already mounted within the target system
        mount "$EFI_PARTITION" /mnt/boot/efi 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "Warning: Failed to mount EFI partition '$EFI_PARTITION' to /mnt/boot/efi." >&2
        else
            echo "  • EFI partition mounted to /mnt/boot/efi."
        fi
    else
        echo "  • EFI partition already mounted within target system. Skipping."
    fi
fi

echo "✅ System successfully mounted to /mnt. Ready for chroot operations."
exit 0