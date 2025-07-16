#!/bin/bash

# Ensure the script is run as root
# While not strictly necessary to *list* mounts, it's good practice for a rescue tool
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Listing all currently mounted filesystems:"

# Use 'findmnt' for a more readable and structured output
findmnt -D -J

if [ $? -eq 0 ]; then
  echo "✅ Filesystems listed successfully."
  exit 0
else
  echo "❌ Failed to list filesystems. Check 'findmnt' utility." >&2
  exit 1
fi