@echo off
echo ===== Pilot Kneeboard Windows Cleanup Script =====
echo This script will remove temporary files and directories.
echo.

REM Ask for confirmation
set /p confirm=Are you sure you want to clean up temporary files? (y/n): 
if /i not "%confirm%"=="y" (
    echo Cleanup cancelled.
    goto end
)

echo Cleaning up Python bytecode files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
del /s /q *.pyd 2>nul

echo Cleaning up Kivy cache files...
if exist "%USERPROFILE%\.kivy\cache" rd /s /q "%USERPROFILE%\.kivy\cache"

echo Cleaning up log files...
del /s /q *.log 2>nul

echo Cleaning up temporary files...
del /s /q *~ 2>nul
del /s /q *.bak 2>nul
del /s /q *.swp 2>nul
del /s /q *.swo 2>nul

echo.
echo ===== Cleanup Complete =====
echo.

:end
pause
