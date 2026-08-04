# Video Meadow 🌾

Video Meadow is a small desktop application for downloading videos through a GUI inspired by the pixel art of farming games. It uses `yt-dlp` to support YouTube and many other compatible websites.

The interface includes:

- background downloads with a progress bar;
- video quality, audio-only, and subtitle options;
- destination folder selection;
- dynamic day/night scenery;
- a pirate-themed desktop icon.

## Requirements 🧰

- Python 3.10 or later;
- Tkinter, normally included with the standard Python installation;
- `yt-dlp[default]`;
- `ffmpeg` and `ffprobe`, required to convert audio-only downloads to MP3.

## Quick start 🚜

If the virtual environment already exists:

```powershell
venv\Scripts\python.exe download_videos.py
```

To create a new environment from scratch:

```powershell
py -m venv venv
venv\Scripts\python.exe -m pip install -U "yt-dlp[default]"
venv\Scripts\python.exe download_videos.py
```

## Windows desktop shortcut 🖥️

For a one-time setup, double-click `setup_video_meadow.bat`. It will:

1. create the local virtual environment;
2. install the Python dependencies from `requirements.txt`;
3. check whether `ffmpeg` is available for MP3 conversion;
4. create a `Video Meadow` shortcut on the desktop using the bundled icon.

After setup, launch the app by double-clicking the desktop shortcut or `run_video_meadow.bat`.

`ffmpeg` and `ffprobe` must be available in `PATH` to use `AUDIO ONLY` and convert the result to MP3.

## Usage 🎬

1. Launch the application.
2. Paste the video URL into the `VIDEO LINK` field.
3. Choose a destination folder, or keep the default one.
4. Click `CHECK VIDEO` to inspect the formats and subtitles available for that link.
5. Use the `QUALITY` button to cycle through the available quality levels.
6. Choose a subtitle language from the `SUBTITLES` dropdown.
7. Toggle the separate `AUDIO ONLY` button to download just the best available audio track and convert it to MP3.
8. Optionally set the night mode start time using the `HH:MM` format.
9. Click `DOWNLOAD VIDEO` or `DOWNLOAD AUDIO` and wait for the download to finish.

The default folder is the directory from which the application is launched. Each download is organized into a subfolder using this format:

```text
[Video title] [Video ID]/[Video title] [Video ID].mp4
```

Video downloads are saved as MP4 files; audio-only downloads are converted to 192 kbps MP3 files.

## Credits 💛

Video Meadow is powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), an open-source project maintained by its community and contributors. Many thanks to the yt-dlp team for their excellent work.

Please download only content you are authorized to save, and respect the terms of service of the websites you use.
