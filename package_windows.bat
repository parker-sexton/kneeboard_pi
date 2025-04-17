@echo off
echo ===== Pilot Kneeboard Windows Packaging Script =====
echo This script will create a distributable zip file of the application.
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available.'" > nul 2>&1
if %errorlevel% neq 0 (
    echo PowerShell is not available. This script requires PowerShell.
    echo Please ensure PowerShell is installed on your system.
    pause
    exit /b 1
)

set PACKAGE_NAME=pilot_kneeboard
set VERSION=1.0.0
set FULL_PACKAGE_NAME=%PACKAGE_NAME%_%VERSION%

echo Creating temporary directory...
set TEMP_DIR=%TEMP%\%FULL_PACKAGE_NAME%_build
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\%FULL_PACKAGE_NAME%"

echo Copying files...
copy kneeboard_gui.py "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy README.md "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy LICENSE.txt "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy requirements.txt "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy install.sh "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy setup_service.sh "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy kneeboard.service "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy run_kneeboard.bat "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"
copy install_windows.bat "%TEMP_DIR%\%FULL_PACKAGE_NAME%\"

echo Creating zip archive using PowerShell...
powershell -Command "& {Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::CreateFromDirectory('%TEMP_DIR%\%FULL_PACKAGE_NAME%', '%CD%\%FULL_PACKAGE_NAME%.zip');}"

if %errorlevel% neq 0 (
    echo Failed to create zip file.
    echo You may need to install the .NET Framework.
    goto cleanup
)

echo.
echo ===== Packaging Complete =====
echo Package created: %FULL_PACKAGE_NAME%.zip
echo.
echo You can distribute this zip file to other users.
echo They can extract it and follow the installation instructions in the README.md file.
echo.

:cleanup
echo Cleaning up temporary files...
rmdir /s /q "%TEMP_DIR%"

pause
