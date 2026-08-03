# Video Meadow 🌾

Video Meadow is a small desktop application for downloading videos through a GUI inspired by the pixel art of farming games. It uses `yt-dlp` to support YouTube and many other compatible websites.

The interface includes:

- background downloads with a progress bar;
- destination folder selection;
- dynamic day/night scenery;
- pixel-art sea, pirate ship, CDs, and DVDs;
- a clickable link to the `yt-dlp` project and friendly credits.

## Requirements 🧰

- Python 3.10 or later;
- Tkinter, normally included with the standard Python installation;
- `yt-dlp[default]`.

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

## Usage 🎬

1. Launch the application.
2. Paste the video URL into the `VIDEO LINK` field.
3. Choose a destination folder, or keep the default one.
4. Click `CHECK VIDEO` to inspect the formats and subtitles available for that link.
5. Use the `QUALITY` button to cycle through the available quality levels.
6. Use the `SUBTITLES` button to choose from the available subtitle languages.
7. Optionally set the night mode start time using the `HH:MM` format.
8. Click `DOWNLOAD VIDEO` and wait for the download to finish.

The default folder is the directory from which the application is launched. Each video is organized into a subfolder using this format:

```text
[Video title] [Video ID]/[Video title] [Video ID].mp4
```

## Credits 💛

Video Meadow is powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), an open-source project maintained by its community and contributors. Many thanks to the yt-dlp team for their excellent work.

Please download only content you are authorized to save, and respect the terms of service of the websites you use.
