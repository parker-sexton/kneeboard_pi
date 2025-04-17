#!/bin/bash
# Setup script for Pilot Kneeboard systemd service
# This script helps install the kneeboard application as a systemd service

echo "===== Pilot Kneeboard Service Setup ====="
echo "This script will set up the kneeboard application to run automatically on boot using systemd."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo:"
    echo "sudo ./setup_service.sh"
    exit 1
fi

# Get the current directory
CURRENT_DIR=$(pwd)

# Check if kneeboard_gui.py exists
if [ ! -f "$CURRENT_DIR/kneeboard_gui.py" ]; then
    echo "Error: kneeboard_gui.py not found in the current directory."
    echo "Please run this script from the directory containing the kneeboard application."
    exit 1
fi

# Check if kneeboard.service exists
if [ ! -f "$CURRENT_DIR/kneeboard.service" ]; then
    echo "Error: kneeboard.service not found in the current directory."
    exit 1
fi

# Get the current user
CURRENT_USER=$(logname || whoami)
echo "Setting up service to run as user: $CURRENT_USER"

# Create a temporary service file with the correct paths
TMP_SERVICE_FILE=$(mktemp)
cat "$CURRENT_DIR/kneeboard.service" > "$TMP_SERVICE_FILE"

# Update the paths in the service file
sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $CURRENT_DIR/kneeboard_gui.py|" "$TMP_SERVICE_FILE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_DIR|" "$TMP_SERVICE_FILE"
sed -i "s|User=.*|User=$CURRENT_USER|" "$TMP_SERVICE_FILE"

# Copy the modified service file to the systemd directory
cp "$TMP_SERVICE_FILE" /etc/systemd/system/kneeboard.service
rm "$TMP_SERVICE_FILE"

echo "Service file installed to /etc/systemd/system/kneeboard.service"

# Reload systemd to recognize the new service
systemctl daemon-reload
echo "Systemd configuration reloaded"

# Enable the service to start on boot
systemctl enable kneeboard.service
echo "Service enabled to start on boot"

# Ask if the user wants to start the service now
read -p "Do you want to start the kneeboard service now? (y/n): " start_now
if [ "$start_now" = "y" ]; then
    systemctl start kneeboard.service
    echo "Service started"
    
    # Check if the service is running
    if systemctl is-active --quiet kneeboard.service; then
        echo "Kneeboard service is running successfully!"
    else
        echo "Warning: Service may not have started correctly."
        echo "Check status with: sudo systemctl status kneeboard.service"
    fi
else
    echo "Service will start on next boot"
    echo "You can manually start it with: sudo systemctl start kneeboard.service"
fi

echo ""
echo "===== Setup Complete ====="
echo "The kneeboard application will now start automatically on boot."
echo "You can manage the service with these commands:"
echo "  - Check status: sudo systemctl status kneeboard.service"
echo "  - Start service: sudo systemctl start kneeboard.service"
echo "  - Stop service: sudo systemctl stop kneeboard.service"
echo "  - Disable autostart: sudo systemctl disable kneeboard.service"
echo ""
echo "Thank you for setting up the Pilot Kneeboard Application!"
echo "Fly safe!"
