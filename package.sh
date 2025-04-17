#!/bin/bash
# Packaging script for Pilot Kneeboard Application
# This script creates a distributable zip file of the application

echo "===== Pilot Kneeboard Packaging Script ====="
echo "This script will create a distributable zip file of the application."
echo ""

# Check if zip is installed
if ! command -v zip &> /dev/null; then
    echo "The 'zip' command is not installed. Please install it first:"
    echo "sudo apt install zip"
    exit 1
fi

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_NAME="pilot_kneeboard"
VERSION="1.0.0"
FULL_PACKAGE_NAME="${PACKAGE_NAME}_${VERSION}"
PACKAGE_DIR="${TEMP_DIR}/${FULL_PACKAGE_NAME}"

echo "Creating package directory structure..."
mkdir -p "${PACKAGE_DIR}"

# Copy all necessary files
echo "Copying files..."
cp kneeboard_gui.py "${PACKAGE_DIR}/"
cp README.md "${PACKAGE_DIR}/"
cp LICENSE.txt "${PACKAGE_DIR}/"
cp requirements.txt "${PACKAGE_DIR}/"
cp install.sh "${PACKAGE_DIR}/"
cp setup_service.sh "${PACKAGE_DIR}/"
cp kneeboard.service "${PACKAGE_DIR}/"
cp run_kneeboard.bat "${PACKAGE_DIR}/"
cp install_windows.bat "${PACKAGE_DIR}/"

# Create the zip file
echo "Creating zip archive..."
cd "${TEMP_DIR}"
zip -r "${FULL_PACKAGE_NAME}.zip" "${FULL_PACKAGE_NAME}"

# Move the zip file to the current directory
mv "${FULL_PACKAGE_NAME}.zip" "$(pwd)/"

# Clean up
rm -rf "${TEMP_DIR}"

echo ""
echo "===== Packaging Complete ====="
echo "Package created: ${FULL_PACKAGE_NAME}.zip"
echo ""
echo "You can distribute this zip file to other users."
echo "They can extract it and follow the installation instructions in the README.md file."
echo ""
