#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root."
  exit 1
fi

echo "Checking for pacman backup package cache..."

latest_pkg=$(ls -t /var/cache/pacman/pkg/*.pkg.tar.zst 2>/dev/null | head -n 1)

if [ -z "$latest_pkg" ]; then
  echo "No package cache found to rollback."
  exit 1
fi

pkg_name=$(basename "$latest_pkg" | cut -d'-' -f1)

echo "Rolling back package: $pkg_name"
yes | pacman -U "$latest_pkg"

echo "Rollback complete. You may need to reboot."
