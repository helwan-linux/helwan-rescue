#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

echo "Attempting to fix common directory permissions..."

# Fix home directory permissions for all users
# Changed to 755 for home directories to allow others to cd into them for listing files (e.g. for web servers, but still protecting contents)
# If strict 700 is preferred, change 755 to 700
echo "  • Fixing /home directory permissions..."
find /home -maxdepth 1 -type d -print0 | xargs -0 chmod 755 2>/dev/null
# Fix permissions and ownership for the current logged-in user's home directory
# Using logname is better for active user context, but it fails if run from a different TTY or without a logged-in user
# For a rescue environment, we often need to fix for a *specific* user or all users.
# Let's add a safer loop for existing users
for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        username=$(basename "$user_home")
        echo "    - Setting ownership for $username's home directory..."
        chown -R "$username":"$username" "$user_home" 2>/dev/null
        echo "    - Setting permissions for $username's home directory to 700..."
        chmod 700 "$user_home" 2>/dev/null
    fi
done

# Fix root permissions
echo "  • Fixing /root directory permissions..."
chmod 700 /root 2>/dev/null
chown -R root:root /root 2>/dev/null

# Fix /tmp permissions
echo "  • Fixing /tmp directory permissions..."
chmod 1777 /tmp 2>/dev/null

if [ $? -eq 0 ]; then
  echo "✅ Permissions fixed successfully."
  exit 0
else
  echo "❌ Permissions fix completed with potential issues. Please check logs." >&2
  exit 1
fi