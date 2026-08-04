@echo off
setlocal

cd /d "%~dp0"
set "APP_DIR=%~dp0"
set "PYTHON_EXE=%APP_DIR%venv\Scripts\python.exe"

where py >nul 2>&1
if errorlevel 1 (
    echo Python was not found. Install Python 3.10 or later and try again.
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo Creating the virtual environment...
    py -m venv "%APP_DIR%venv"
    if errorlevel 1 (
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
)

echo Installing Python dependencies...
"%PYTHON_EXE%" -m pip install -U pip
"%PYTHON_EXE%" -m pip install -r "%APP_DIR%requirements.txt"
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: ffmpeg was not found in PATH.
    echo Video downloads will work, but AUDIO ONLY to MP3 requires ffmpeg.
)

echo Creating the desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%create_video_meadow_shortcut.ps1" -AppDirectory "%CD%"
if errorlevel 1 (
    echo Could not create the desktop shortcut.
    pause
    exit /b 1
)

echo.
echo Video Meadow is ready. You can launch it from the desktop shortcut.
pause
