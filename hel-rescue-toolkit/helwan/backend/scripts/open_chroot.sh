#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "This requires root."
  exit 1
fi

echo "Detecting mounted partitions..."
root_partition=$(lsblk -lpo NAME,MOUNTPOINT | grep ' /$' | awk '{print $1}')

if [ -z "$root_partition" ]; then
  echo "Root partition not found."
  exit 1
fi

echo "Mounting system in /mnt..."

mount "$root_partition" /mnt 2>/dev/null

for dir in dev proc sys run; do
  mount --bind /$dir /mnt/$dir
done

arch-chroot /mnt
