#!/bin/bash

# Fix permissions for mounted volumes
# This script ensures the streamlit user can write to the mounted directories

# Change ownership of mounted directories to streamlit user
# Check if directories are mounted (not empty from host)
if [ -d "/app/data" ]; then
    # Only fix permissions if the directory is not empty (indicating it's a mount)
    if [ "$(ls -A /app/data 2>/dev/null)" ] || [ "$(stat -c %U /app/data 2>/dev/null)" != "streamlit" ]; then
        echo "Fixing permissions for /app/data..."
        chown -R streamlit:streamlit /app/data
        chmod -R 755 /app/data
    fi
fi

if [ -d "/app/static" ]; then
    # Only fix permissions if the directory is not empty (indicating it's a mount)
    if [ "$(ls -A /app/static 2>/dev/null)" ] || [ "$(stat -c %U /app/static 2>/dev/null)" != "streamlit" ]; then
        echo "Fixing permissions for /app/static..."
        chown -R streamlit:streamlit /app/static
        chmod -R 755 /app/static
    fi
fi

# Execute the command passed to the script
exec "$@"
