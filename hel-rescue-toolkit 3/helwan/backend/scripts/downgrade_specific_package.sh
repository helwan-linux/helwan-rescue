#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

if [ -z "$1" ]; then
    echo "Error: No package name provided. Usage: $0 <package_name>" >&2
    echo "Please provide the name of the package you want to downgrade." >&2
    exit 1
fi

PACKAGE_NAME="$1"

echo "Attempting to downgrade package: $PACKAGE_NAME"

# Find cached versions of the package
CACHED_PKGS=$(ls -t /var/cache/pacman/pkg/"$PACKAGE_NAME"-*.pkg.tar.* 2>/dev/null)

if [ -z "$CACHED_PKGS" ]; then
    echo "Error: No cached versions found for package '$PACKAGE_NAME'." >&2
    echo "Please ensure the package exists in /var/cache/pacman/pkg/." >&2
    exit 1
fi

echo "Available cached versions for '$PACKAGE_NAME':"
versions=()
for pkg_path in $CACHED_PKGS; do
    pkg_basename=$(basename "$pkg_path")
    echo "  - $pkg_basename"
    versions+=("$pkg_basename")
done

echo "Please choose a version to downgrade to from the list above (e.g., 'package-1.0-1-arch.pkg.tar.zst') or type 'cancel':"
read -r SELECTED_PKG_FILE

if [ "$SELECTED_PKG_FILE" = "cancel" ]; then
    echo "Operation cancelled."
    exit 0
fi

SELECTED_PKG_PATH="/var/cache/pacman/pkg/$SELECTED_PKG_FILE"

if [ ! -f "$SELECTED_PKG_PATH" ]; then
    echo "Error: Invalid selection or package file not found: '$SELECTED_PKG_FILE'" >&2
    exit 1
fi

echo "Downgrading to: $SELECTED_PKG_PATH"
pacman -U "$SELECTED_PKG_PATH"

if [ $? -eq 0 ]; then
  echo "✅ Package '$PACKAGE_NAME' downgraded successfully to '$SELECTED_PKG_FILE'."
  echo "   - You may need to reboot if system libraries were affected."
  exit 0
else
  echo "❌ Failed to downgrade package '$PACKAGE_NAME'. Check for dependency issues or invalid package." >&2
  exit 1
fi