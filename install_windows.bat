@echo off
echo ===== Pilot Kneeboard Windows Setup =====
echo This script will install the required dependencies for the Pilot Kneeboard application.
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the PATH.
    echo Please install Python 3.6+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

echo Python is installed. Installing dependencies...
echo.

REM Check if tkinter is available
python -c "import tkinter" > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: tkinter may not be installed with your Python.
    echo The application requires tkinter, which usually comes with Python.
    echo If you encounter errors, please reinstall Python and select the tcl/tk option.
    echo.
    pause
)

REM Install Pillow using pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Failed to install dependencies. Please try again or install manually:
    echo pip install pillow
    pause
    exit /b 1
)

echo.
echo ===== Installation Complete =====
echo.
echo You can now run the application by double-clicking run_kneeboard.bat
echo or by running: python kneeboard_gui.py
echo.
echo Enjoy your digital kneeboard!
echo.

pause
