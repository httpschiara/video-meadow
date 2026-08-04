@echo off
setlocal

cd /d "%~dp0"
set "APP_DIR=%~dp0"
set "PYTHONW=%APP_DIR%venv\Scripts\pythonw.exe"

if not exist "%PYTHONW%" (
    echo Video Meadow is not set up yet.
    echo Run setup_video_meadow.bat first.
    pause
    exit /b 1
)

start "Video Meadow" "%PYTHONW%" "%APP_DIR%download_videos.py"
exit /b 0
