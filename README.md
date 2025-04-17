# Pilot Kneeboard Application

A touchscreen application for pilots to use as a digital kneeboard when flying planes, specifically designed for the Piper Archer aircraft. This application is optimized for use on a Raspberry Pi Zero W 2 with a touchscreen.

## Features

### 1. Squawk Code Selector
- Digital pinpad for entering 4-digit squawk codes
- Default VFR code (1200) pre-set
- Quick access to emergency code (7700)
- Clear button to reset the code

### 2. Piper Archer Reference Information
- Aircraft specifications
- V-speeds reference
- Normal procedures (takeoff and landing)
- Emergency procedures
- Radio frequencies

### 3. Digital Notepad
- Touch-sensitive drawing area for taking notes
- Clear button to erase all notes
- Optimized for stylus/pen input

### 4. Additional Features
- Real-time clock display
- Tab-based interface for easy navigation
- Touch-optimized UI elements

## Requirements

- Python 3.6+
- Kivy 2.0+
- Raspberry Pi Zero W 2 (recommended)
- Touchscreen display

## Installation

### Windows Installation (for testing)

#### Automatic Installation
1. Run the Windows installation script:
   ```
   install_windows.bat
   ```
   
   This script will:
   - Check if Python is installed
   - Install Kivy using pip
   - Provide instructions for running the application

#### Manual Installation
1. Install Python 3.6+ from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. Install Kivy using pip:
   ```
   pip install -r requirements.txt
   ```
   
   Or directly:
   ```
   pip install kivy
   ```

3. Run the application using the batch file:
   ```
   run_kneeboard.bat
   ```

### Raspberry Pi Installation (Recommended)

1. Clone or download this repository to your Raspberry Pi.

2. Run the installation script:
   ```
   chmod +x install.sh
   ./install.sh
   ```
   
   The script will:
   - Install Python and required dependencies
   - Install Kivy
   - Make the application executable
   - Optionally set up autostart on boot

### Manual Installation

If you prefer to install manually:

1. Ensure Python is installed on your Raspberry Pi:
   ```
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. Install Kivy and its dependencies:
   ```
   sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
   sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
   sudo apt install libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev
   sudo apt install python3-dev

   pip3 install kivy
   ```

3. Make the script executable:
   ```
   chmod +x kneeboard_gui.py
   ```

## Running the Application

### Manual Start

#### On Raspberry Pi (Linux)
Run the application with:
```
python3 kneeboard_gui.py
```

#### On Windows (for testing)
Double-click the `run_kneeboard.bat` file or run it from the command prompt:
```
run_kneeboard.bat
```

### Automatic Start on Boot

There are two ways to configure the application to start automatically on boot:

1. **Using the installation script** - The script will offer to set up autostart using the desktop environment.

2. **Using systemd service** - For a more robust solution, especially if running headless:

   a. Using the setup script (recommended):
   ```
   chmod +x setup_service.sh
   sudo ./setup_service.sh
   ```
   
   b. Manual setup:
   ```
   # Copy the service file to the systemd directory
   sudo cp kneeboard.service /etc/systemd/system/
   
   # Edit the service file to match your installation path
   sudo nano /etc/systemd/system/kneeboard.service
   
   # Enable and start the service
   sudo systemctl enable kneeboard.service
   sudo systemctl start kneeboard.service
   ```

## Usage Instructions

### Squawk Code Entry
1. Tap the "Squawk" tab
2. Use the number pad to enter your assigned squawk code
3. Tap "VFR" for the standard VFR code (1200)
4. Tap "EMER" for the emergency code (7700)
5. Tap "Clear" to reset the code

### Reference Information
1. Tap the "Reference" tab
2. Scroll through the available information sections
3. Reference data is organized by category for easy access

### Notepad
1. Tap the "Notepad" tab
2. Use your finger or stylus to write/draw on the screen
3. Tap "Clear Notepad" to erase all content

## Customization

You can customize the application by modifying the `kneeboard_gui.py` file:

- Add additional reference information in the `PiperArcherReference` class
- Modify the window size in the code to match your specific touchscreen dimensions
- Add additional tabs or features as needed

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- Developed for pilots using the Piper Archer aircraft
- Optimized for Raspberry Pi Zero W 2 with touchscreen
