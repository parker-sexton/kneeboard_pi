#!/bin/bash
# Cleanup script for Pilot Kneeboard Application
# This script removes temporary files and directories

echo "===== Pilot Kneeboard Cleanup Script ====="
echo "This script will remove temporary files and directories."
echo ""

# Ask for confirmation
read -p "Are you sure you want to clean up temporary files? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "Cleaning up Python bytecode files..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

echo "Cleaning up Kivy cache files..."
rm -rf ~/.kivy/cache/*

echo "Cleaning up log files..."
find . -name "*.log" -delete

echo "Cleaning up temporary files..."
find . -name "*~" -delete
find . -name "*.bak" -delete
find . -name "*.swp" -delete
find . -name "*.swo" -delete

echo ""
echo "===== Cleanup Complete ====="
echo ""
