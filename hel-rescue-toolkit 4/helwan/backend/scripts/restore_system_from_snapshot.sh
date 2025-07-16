#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to restore system from a snapshot..."
echo "WARNING: This operation can lead to data loss if not used correctly." >&2
echo "         Ensure you have backed up important data." >&2

ROOT_FSTYPE=$(stat -f -c %T /)

if [ "$ROOT_FSTYPE" = "btrfs" ]; then
    echo "  • Btrfs filesystem detected for root (/). Listing available Btrfs snapshots in /.snapshots/..."

    SNAPSHOT_DIR="/.snapshots"
    if [ ! -d "$SNAPSHOT_DIR" ]; then
        echo "Error: Snapshot directory /.snapshots not found." >&2
        exit 1
    fi

    SNAPSHOTS=$(btrfs subvolume list -o / | grep "$SNAPSHOT_DIR" | awk '{print $NF}' | sed "s|^$SNAPSHOT_DIR/||")

    if [ -z "$SNAPSHOTS" ]; then
        echo "Error: No Btrfs snapshots found in $SNAPSHOT_DIR." >&2
        exit 1
    fi

    echo "Available snapshots:"
    select SNAPSHOT_TO_RESTORE in $SNAPSHOTS "Cancel"; do
        if [ "$SNAPSHOT_TO_RESTORE" = "Cancel" ]; then
            echo "Operation cancelled."
            exit 0
        elif [ -n "$SNAPSHOT_TO_RESTORE" ]; then
            break
        else
            echo "Invalid selection. Please try again." >&2
        fi
    done

    echo "Restoring from snapshot: $SNAPSHOT_TO_RESTORE"

    # Important: This operation requires rebooting from a live environment
    # or using a dedicated snapshot management tool.
    # We are demonstrating the core Btrfs commands here.
    # A full restoration typically involves:
    # 1. Booting from a live USB.
    # 2. Mounting the Btrfs root.
    # 3. Deleting the old root subvolume.
    # 4. Renaming the snapshot subvolume to the root subvolume.
    # 5. Regenerating grub/initramfs if necessary.

    echo "  • For Btrfs, a full restore often requires booting from a Live ISO."
    echo "  • The following command sets the default subvolume to your chosen snapshot:"
    echo "    btrfs subvolume set-default $(btrfs subvolume list / | grep "$SNAPSHOT_DIR/$SNAPSHOT_TO_RESTORE" | awk '{print $NF}' | sed 's/.*id //')"
    echo "  • After setting the default, you will need to reboot and potentially regenerate GRUB configuration."
    echo ""
    echo "Warning: This script does NOT perform the full reboot/reconfigure steps." >&2
    echo "         It guides you on the Btrfs command to set the default subvolume." >&2
    echo "✅ Operation guided successfully. Please follow the instructions above."
    exit 0
else
    echo "Error: Root filesystem is '$ROOT_FSTYPE', which is not supported by this snapshot restore script." >&2
    echo "  • Restore operation failed or is not supported for your current filesystem type." >&2
    exit 1
fi