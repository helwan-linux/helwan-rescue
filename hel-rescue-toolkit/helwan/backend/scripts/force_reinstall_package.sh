#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

if [ -z "$1" ]; then
    echo "Error: No package name provided. Usage: $0 <package_name>" >&2
    echo "Please provide the name of the package you want to reinstall." >&2
    exit 1
fi

PACKAGE_NAME="$1"

echo "Attempting to force reinstall package: $PACKAGE_NAME"

# Check if the package is installed
if ! pacman -Qs "$PACKAGE_NAME" >/dev/null 2>&1; then
    echo "Error: Package '$PACKAGE_NAME' is not installed." >&2
    exit 1
fi

# Force reinstall using --overwrite "*" to handle file conflicts
# Using --noconfirm to avoid user interaction for pacman.
# Consider adding a warning in the GUI if --noconfirm is used.
pacman -S "$PACKAGE_NAME" --noconfirm --overwrite "*"

if [ $? -eq 0 ]; then
  echo "✅ Package '$PACKAGE_NAME' reinstalled successfully."
  exit 0
else
  echo "❌ Failed to reinstall package '$PACKAGE_NAME'. Check for errors in pacman output." >&2
  exit 1
fi