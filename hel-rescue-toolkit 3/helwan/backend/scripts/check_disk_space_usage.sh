#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Checking disk space usage:"

# Use 'df -h' for human-readable output
df -h

echo ""
echo "Listing top 10 largest directories in / (may take some time):"
# Find top 10 largest directories from root
du -sh /* 2>/dev/null | sort -rh | head -n 10

echo "✅ Disk space usage check complete."
exit 0