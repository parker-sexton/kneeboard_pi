#!/bin/bash
# Installation script for Pilot Kneeboard Application
# Designed for Raspberry Pi Zero W 2 with touchscreen

echo "===== Pilot Kneeboard Application Installer ====="
echo "This script will install the necessary dependencies for the Pilot Kneeboard application."
echo "Designed for Raspberry Pi Zero W 2 with touchscreen."
echo ""

# Check if running on Raspberry Pi
if [ ! -f /etc/os-release ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi."
    echo "This application is optimized for Raspberry Pi Zero W 2."
    read -p "Continue anyway? (y/n): " continue_install
    if [ "$continue_install" != "y" ]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

echo "Updating package lists..."
sudo apt update

echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip

echo "Installing Kivy dependencies..."
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev
sudo apt install -y python3-dev

echo "Installing Kivy..."
pip3 install kivy

echo "Making kneeboard_gui.py executable..."
chmod +x kneeboard_gui.py

echo ""
echo "===== Installation Complete ====="
echo ""
echo "To run the application, use:"
echo "python3 kneeboard_gui.py"
echo ""

# Ask about autostart
read -p "Would you like to set up the kneeboard to start automatically on boot? (y/n): " setup_autostart
if [ "$setup_autostart" = "y" ]; then
    echo "Setting up autostart..."
    
    # Create autostart directory if it doesn't exist
    mkdir -p ~/.config/autostart
    
    # Create desktop entry for autostart
    cat > ~/.config/autostart/kneeboard.desktop << EOF
[Desktop Entry]
Type=Application
Name=Pilot Kneeboard
Comment=Digital kneeboard for pilots
Exec=python3 $(pwd)/kneeboard_gui.py
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
    
    echo "Autostart configured. The kneeboard will start automatically on next boot."
    echo "You may need to enable the desktop environment on your Raspberry Pi"
    echo "using 'sudo raspi-config' if you haven't already done so."
fi

echo ""
echo "Thank you for installing the Pilot Kneeboard Application!"
echo "Fly safe!"
