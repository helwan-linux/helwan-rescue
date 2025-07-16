#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

# Check if a username is provided as an argument
if [ -z "$1" ]; then
  echo "Error: No username provided. Usage: $0 <username>" >&2
  echo "Please provide a username for the new user." >&2
  exit 1
fi

NEW_USERNAME="$1"

# Check if the user already exists
if id -u "$NEW_USERNAME" >/dev/null 2>&1; then
    echo "Error: User '$NEW_USERNAME' already exists on this system." >&2
    exit 1
fi

echo "Attempting to create new user: $NEW_USERNAME"

# Create the new user with a home directory and default shell
useradd -m -s /bin/bash "$NEW_USERNAME"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create user '$NEW_USERNAME'. Please check logs." >&2
    exit 1
fi

echo "  • User '$NEW_USERNAME' created successfully."

echo "  • Setting password for user '$NEW_USERNAME'..."
passwd "$NEW_USERNAME"

if [ $? -ne 0 ]; then
    echo "❌ Failed to set password for user '$NEW_USERNAME'. User created, but password not set." >&2
    exit 1
fi

echo "  • Adding user '$NEW_USERNAME' to wheel group (for sudo access)..."
usermod -aG wheel "$NEW_USERNAME"

if [ $? -eq 0 ]; then
  echo "✅ User '$NEW_USERNAME' created and configured successfully."
  echo "   - Home directory: /home/$NEW_USERNAME"
  echo "   - Default shell: /bin/bash"
  echo "   - Added to 'wheel' group (for sudo)."
  exit 0
else
  echo "❌ User '$NEW_USERNAME' created, but failed to add to 'wheel' group." >&2
  exit 1
fi