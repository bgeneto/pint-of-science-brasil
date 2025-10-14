#!/bin/bash

# Fix permissions for mounted volumes
# This script ensures the streamlit user can write to the mounted directories

echo "Checking and fixing volume permissions..."

# Change ownership of mounted directories to streamlit user
if [ -d "/app/data" ]; then
    # Check current owner and fix if needed
    current_owner=$(stat -c %U /app/data 2>/dev/null || echo "unknown")
    echo "Current owner of /app/data: $current_owner"

    if [ "$current_owner" != "streamlit" ]; then
        echo "Fixing permissions for /app/data..."
        chown -R streamlit:streamlit /app/data
        chmod -R 755 /app/data
        echo "Fixed permissions for /app/data"
    fi
fi

if [ -d "/app/static" ]; then
    # Check current owner and fix if needed
    current_owner=$(stat -c %U /app/static 2>/dev/null || echo "unknown")
    echo "Current owner of /app/static: $current_owner"

    if [ "$current_owner" != "streamlit" ]; then
        echo "Fixing permissions for /app/static..."
        chown -R streamlit:streamlit /app/static
        chmod -R 755 /app/static
        echo "Fixed permissions for /app/static"
    fi
fi

# Switch to streamlit user and execute the command
echo "Switching to streamlit user and executing: $@"
exec su-exec streamlit:streamlit "$@"
