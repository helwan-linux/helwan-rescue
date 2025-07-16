#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to create a system snapshot..."

# Detect root filesystem type
ROOT_FSTYPE=$(stat -f -c %T /)

if [ "$ROOT_FSTYPE" = "btrfs" ]; then
    echo "  • Btrfs filesystem detected for root (/). Creating Btrfs snapshot..."
    SNAPSHOT_DIR="/.snapshots"
    SNAPSHOT_NAME="root_$(date +%Y-%m-%d_%H-%M-%S)"

    # Ensure .snapshots directory exists
    mkdir -p "$SNAPSHOT_DIR"

    # Create the Btrfs snapshot
    btrfs subvolume snapshot -r / "$SNAPSHOT_DIR/$SNAPSHOT_NAME"

    if [ $? -eq 0 ]; then
        echo "✅ Btrfs snapshot '$SNAPSHOT_NAME' created successfully in $SNAPSHOT_DIR."
        echo "   - To restore, you might use 'btrfs subvolume set-default' and reboot, or a dedicated tool like 'snapper'."
        exit 0
    else
        echo "❌ Failed to create Btrfs snapshot. Check Btrfs tools and permissions." >&2
        exit 1
    fi
else
    echo "Warning: Root filesystem is '$ROOT_FSTYPE', which does not natively support easy snapshots." >&2
    echo "  • This script currently supports Btrfs snapshots. For other filesystems," >&2
    echo "    please consider using tools like 'Timeshift' or 'Snapper' (if configured)." >&2
    echo "  • Snapshot creation failed or is not supported for your current filesystem type." >&2
    exit 1
fi