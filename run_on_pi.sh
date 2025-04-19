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

# Check if Kivy is installed
if ! pip3 list | grep -q "kivy"; then
    echo "Kivy is not installed. Installing..."
    sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
    sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
    sudo apt install -y libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev
    sudo apt install -y python3-dev
    pip3 install kivy
fi

# Make sure the script is executable
chmod +x kneeboard_gui.py

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

# Reset display orientation when the app exits
if command -v xrandr &> /dev/null; then
    echo "Resetting display orientation..."
    xrandr --output HDMI-1 --rotate normal || true
    xrandr --output $(xrandr | grep " connected" | head -n 1 | cut -d " " -f1) --rotate normal || true
fi

echo "Application closed."
