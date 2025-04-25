#!/bin/bash
# Script to run the Pilot Kneeboard application on Raspberry Pi
# This script ensures all dependencies are installed and runs the app in fullscreen mode

echo "===== Pilot Kneeboard Launcher ====="
echo "This script will launch the Pilot Kneeboard application on your Raspberry Pi."
echo ""

# Check if running on Raspberry Pi
if [ ! -f /etc/os-release ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi."
    echo "This application is optimized for Raspberry Pi with touchscreen."
    read -p "Continue anyway? (y/n): " continue_run
    if [ "$continue_run" != "y" ]; then
        echo "Launch cancelled."
        exit 1
    fi
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# Check if tkinter is installed
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter is not installed. Installing..."
    sudo apt update
    sudo apt install -y --fix-broken python3-tk
fi

# Check if PIL is installed
if ! python3 -c "from PIL import Image, ImageTk" &> /dev/null; then
    echo "Pillow is not installed. Installing..."
    sudo apt install -y --fix-broken python3-pil python3-pil.imagetk
    pip3 install -r requirements.txt --break-system-packages
fi

# Make sure the script is executable
chmod +x kneeboard_gui.py

# Check if running in headless mode
if [ -z "$DISPLAY" ]; then
    echo "Running in headless mode..."
    export HEADLESS=1
    
    # Make sure required packages for headless operation are installed
    if ! dpkg -l | grep -q "xvfb"; then
        echo "Installing X virtual framebuffer for headless operation..."
        sudo apt install -y --fix-broken xvfb x11-xserver-utils
    fi
    
    # Run the application with Xvfb
    echo "Starting Pilot Kneeboard application in headless mode..."
    xvfb-run -a python3 kneeboard_gui.py
else
    # Set display to portrait mode if connected to a display
    if command -v xrandr &> /dev/null; then
        echo "Setting display to portrait orientation..."
        xrandr --output HDMI-1 --rotate right || true
        # If the above fails, try with the primary display
        xrandr --output $(xrandr | grep " connected" | head -n 1 | cut -d " " -f1) --rotate right || true
    fi

    # Run the application
    echo "Starting Pilot Kneeboard application..."
    python3 kneeboard_gui.py
fi

# Reset display orientation when the app exits
if command -v xrandr &> /dev/null; then
    echo "Resetting display orientation..."
    xrandr --output HDMI-1 --rotate normal || true
    xrandr --output $(xrandr | grep " connected" | head -n 1 | cut -d " " -f1) --rotate normal || true
fi

echo "Application closed."
