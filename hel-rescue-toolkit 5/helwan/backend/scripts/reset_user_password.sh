#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Root access required for this operation." >&2
  exit 1
fi

# Check if a username is provided as an argument
if [ -z "$1" ]; then
  echo "Error: No username provided. Usage: $0 <username>" >&2
  echo "Please provide the username whose password you want to reset." >&2
  exit 1
fi

USERNAME="$1"

# Check if the user exists
if ! id -u "$USERNAME" >/dev/null 2>&1; then
    echo "Error: User '$USERNAME' does not exist on this system." >&2
    exit 1
fi

echo "Attempting to reset password for user: $USERNAME"

# Use `passwd` command to reset password.
# It will prompt for the new password. The GUI should ideally handle this input.
# For a simple script, it will block until input.
passwd "$USERNAME"

if [ $? -eq 0 ]; then
  echo "✅ Password for user '$USERNAME' has been successfully reset."
  exit 0
else
  echo "❌ Failed to reset password for user '$USERNAME'. Please check for errors." >&2
  exit 1
fi