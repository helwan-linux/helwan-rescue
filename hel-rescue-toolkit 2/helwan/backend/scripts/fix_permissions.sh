#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Root access required."
  exit 1
fi

echo "Fixing home directory permissions..."
chmod 700 /home/* 2>/dev/null
chown -R $(logname):$(logname) /home/$(logname)

echo "Fixing root permissions..."
chmod 700 /root
chown -R root:root /root

echo "Fixing /tmp permissions..."
chmod 1777 /tmp

echo "Permissions fixed."
