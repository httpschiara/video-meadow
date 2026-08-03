from __future__ import annotations

import queue
import threading
import tkinter as tk
import webbrowser
from datetime import datetime, time
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

import yt_dlp
from yt_dlp.utils import DownloadError, UnsupportedError


APP_TITLE = "Video Meadow"


class VideoMeadow(tk.Tk):
    """Small desktop interface for downloading a single video."""

    COLORS = {
        "sky": "#bfe5e4",
        "sky_deep": "#a8d6d8",
        "cream": "#fff8e8",
        "paper": "#fffdf4",
        "ink": "#4e4438",
        "muted": "#837465",
        "brown": "#765440",
        "brown_dark": "#573d31",
        "green": "#6f9d52",
        "green_dark": "#4e773e",
        "gold": "#eab95d",
        "red": "#c86f5e",
        "line": "#d8c9aa",
    }

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x650")
        self.minsize(680, 570)
        self.configure(bg=self.COLORS["sky"])

        self.url_var = tk.StringVar()
        self.folder_var = tk.StringVar(value=str(Path.cwd()))
        self.night_start_var = tk.StringVar(value="20:00")
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready for the next harvest")
        self.detail_var = tk.StringVar(value="Paste a link and press DOWNLOAD VIDEO")
        self.queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.downloading = False

        self._configure_styles()
        self._build_interface()
        self.night_start_var.trace_add("write", self._on_night_time_changed)
        self.after(100, self._process_events)
        self.after(30_000, self._refresh_sky)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Meadow.Horizontal.TProgressbar",
            troughcolor=self.COLORS["sky_deep"],
            background=self.COLORS["green"],
            bordercolor=self.COLORS["sky_deep"],
            lightcolor=self.COLORS["green"],
            darkcolor=self.COLORS["green_dark"],
            thickness=18,
        )
        style.configure(
            "Meadow.TButton",
            background=self.COLORS["green"],
            foreground="#fffdf4",
            bordercolor=self.COLORS["green_dark"],
            focusthickness=0,
            padding=(16, 10),
            font=("Courier New", 10, "bold"),
        )
        style.map(
            "Meadow.TButton",
            background=[("active", self.COLORS["green_dark"]), ("disabled", "#9eaf91")],
        )
        style.configure(
            "Folder.TButton",
            background=self.COLORS["gold"],
            foreground=self.COLORS["brown_dark"],
            bordercolor="#c9973d",
            focusthickness=0,
            padding=(10, 8),
            font=("Courier New", 9, "bold"),
        )
        style.map("Folder.TButton", background=[("active", "#f0c976")])

    def _build_interface(self) -> None:
        self._build_header()

        body = tk.Frame(self, bg=self.COLORS["cream"], padx=34, pady=24)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="NEW TASK",
            bg=self.COLORS["cream"],
            fg=self.COLORS["brown"],
            font=("Courier New", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        self._field_label(body, "VIDEO LINK:")
        url_row = tk.Frame(body, bg=self.COLORS["cream"])
        url_row.pack(fill="x", pady=(3, 17))
        self.url_entry = tk.Entry(
            url_row,
            textvariable=self.url_var,
            bg=self.COLORS["paper"],
            fg=self.COLORS["ink"],
            insertbackground=self.COLORS["brown"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=self.COLORS["line"],
            highlightcolor=self.COLORS["green"],
            font=("Courier New", 11),
        )
        self.url_entry.pack(fill="x", ipady=9)
        self.url_entry.focus_set()
        self.url_entry.bind("<Return>", lambda _event: self.start_download())

        self._field_label(body, "SAVE LOCATION:")
        folder_row = tk.Frame(body, bg=self.COLORS["cream"])
        folder_row.pack(fill="x", pady=(3, 22))
        tk.Entry(
            folder_row,
            textvariable=self.folder_var,
            bg=self.COLORS["paper"],
            fg=self.COLORS["muted"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=self.COLORS["line"],
            highlightcolor=self.COLORS["gold"],
            font=("Courier New", 9),
        ).pack(side="left", fill="x", expand=True, ipady=8)
        self.folder_button = ttk.Button(
            folder_row, text="CHOOSE FOLDER", command=self.choose_folder, style="Folder.TButton"
        )
        self.folder_button.pack(side="left", padx=(10, 0))

        settings = tk.Frame(body, bg=self.COLORS["cream"])
        settings.pack(fill="x", pady=(0, 20))
        self._field_label(settings, "NIGHT MODE STARTS AT:")
        night_row = tk.Frame(settings, bg=self.COLORS["cream"])
        night_row.pack(fill="x", pady=(3, 0))
        tk.Entry(
            night_row,
            textvariable=self.night_start_var,
            width=8,
            bg=self.COLORS["paper"],
            fg=self.COLORS["ink"],
            insertbackground=self.COLORS["brown"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=self.COLORS["line"],
            highlightcolor=self.COLORS["gold"],
            justify="center",
            font=("Courier New", 10, "bold"),
        ).pack(side="left", ipady=7)
        tk.Label(
            night_row,
            text="  (HH:MM format)  ...the moon and stars will appear automatically!",
            bg=self.COLORS["cream"],
            fg=self.COLORS["muted"],
            font=("Courier New", 8),
            anchor="w",
        ).pack(side="left")

        self._build_progress_card(body)

        actions = tk.Frame(body, bg=self.COLORS["cream"])
        actions.pack(fill="x", pady=(21, 0))
        self.download_button = ttk.Button(
            actions, text="DOWNLOAD VIDEO  ▶", command=self.start_download, style="Meadow.TButton"
        )
        self.download_button.pack(side="left")
        self.open_button = ttk.Button(
            actions, text="OPEN FOLDER", command=self.open_folder, style="Folder.TButton"
        )
        self.open_button.pack(side="right")

        tip_row = tk.Frame(body, bg=self.COLORS["cream"])
        tip_row.pack(fill="x", pady=(16, 0))
        tk.Label(
            tip_row,
            text="Tip: paste links from YouTube and all sites supported by ",
            bg=self.COLORS["cream"],
            fg=self.COLORS["muted"],
            font=("Courier New", 8),
            anchor="w",
        ).pack(side="left")
        ytdlp_link = tk.Label(
            tip_row,
            text="yt-dlp",
            bg=self.COLORS["cream"],
            fg=self.COLORS["brown"],
            cursor="hand2",
            font=("Courier New", 8, "bold", "underline"),
        )
        ytdlp_link.pack(side="left")
        ytdlp_link.bind("<Button-1>", lambda _event: self.open_ytdlp_link())
        tk.Label(
            tip_row,
            text=".",
            bg=self.COLORS["cream"],
            fg=self.COLORS["muted"],
            font=("Courier New", 8),
        ).pack(side="left")
        tk.Label(
            body,
            text="Made with thanks to the yt-dlp team ✦",
            bg=self.COLORS["cream"],
            fg=self.COLORS["brown"],
            font=("Courier New", 8, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

    def _build_header(self) -> None:
        header = tk.Canvas(self, height=150, bg=self.COLORS["sky"], highlightthickness=0)
        header.pack(fill="x")
        header.bind("<Configure>", self._draw_header)
        self.header_canvas = header

    def _draw_header(self, _event: tk.Event | None = None) -> None:
        canvas = self.header_canvas
        width = max(canvas.winfo_width(), 680)
        canvas.delete("all")
        night = self._is_night()
        sky = "#182b45" if night else self.COLORS["sky"]
        hill = "#203b3b" if night else self.COLORS["green_dark"]
        grass = "#3f6948" if night else self.COLORS["green"]
        sea = "#2a5a72" if night else "#62aebc"
        sea_light = "#4d8ca5" if night else "#8bcbd0"
        canvas.configure(bg=sky)

        # Blocky hills and grass for a light pixel-art atmosphere.
        canvas.create_rectangle(0, 92, width, 127, fill=sea, outline="")
        canvas.create_rectangle(0, 92, width, 95, fill=sea_light, outline="")
        for x in range(12, width, 57):
            canvas.create_rectangle(x, 104 + (x % 3) * 3, x + 21, 106 + (x % 3) * 3, fill=sea_light, outline="")
            canvas.create_rectangle(x + 28, 115 + (x % 4) * 2, x + 40, 117 + (x % 4) * 2, fill=sea_light, outline="")
        canvas.create_polygon(
            0, 115, 95, 76, 178, 109, 275, 63, 382, 111, 480, 73, 590, 111, 700, 55, width, 108, width, 127, 0, 127,
            fill=hill, outline="",
        )
        self._draw_pirate_ship(canvas, width - 210, 76, night)
        canvas.create_rectangle(0, 124, width, 150, fill=grass, outline="")
        for x in range(15, width, 34):
            canvas.create_rectangle(x, 135, x + 3, 140, fill="#88a55e" if night else "#a4bd62", outline="")
            canvas.create_rectangle(x + 8, 143, x + 13, 147, fill="#31553e" if night else "#598b48", outline="")
        self._draw_media_on_grass(canvas, width, night)

        if night:
            self._draw_night_sky(canvas, width)
        else:
            canvas.create_oval(width - 128, 18, width - 80, 66, fill=self.COLORS["gold"], outline="")
            self._cloud(canvas, 62, 32, sky)
            self._cloud(canvas, width - 295, 41, sky)

        canvas.create_text(
            36, 35, text="VIDEO MEADOW", anchor="w", fill="#fff1c4" if night else self.COLORS["brown_dark"],
            font=("Courier New", 22, "bold"),
        )
        canvas.create_text(
            38, 55, text="your little video barn", anchor="w", fill="#d5ddb1" if night else self.COLORS["ink"],
            font=("Courier New", 10),
        )

    @staticmethod
    def _draw_pirate_ship(canvas: tk.Canvas, x: int, y: int, night: bool) -> None:
        """Draw a small pirate ship on the horizon line."""
        hull = "#1b2734" if night else "#4b352e"
        wood = "#302b32" if night else "#765440"
        sail = "#e2d7b1" if night else "#f6e7bd"
        flag = "#9e554b" if night else "#9d4439"
        skull = "#26313a" if night else "#5a4033"

        canvas.create_polygon(x, y + 11, x + 38, y + 11, x + 31, y + 18, x + 8, y + 18, fill=hull, outline="")
        canvas.create_rectangle(x + 18, y - 19, x + 21, y + 12, fill=wood, outline="")
        canvas.create_polygon(x + 17, y - 15, x + 3, y + 7, x + 17, y + 7, fill=sail, outline="")
        canvas.create_polygon(x + 22, y - 8, x + 35, y + 6, x + 22, y + 6, fill=sail, outline="")
        canvas.create_polygon(x + 21, y - 19, x + 31, y - 16, x + 21, y - 12, fill=flag, outline="")
        # Pixel-art skull on the main sail.
        canvas.create_rectangle(x + 25, y - 2, x + 31, y + 3, fill=skull, outline="")
        canvas.create_rectangle(x + 27, y + 3, x + 29, y + 5, fill=skull, outline="")
        canvas.create_rectangle(x + 26, y - 1, x + 27, y, fill=sail, outline="")
        canvas.create_rectangle(x + 29, y - 1, x + 30, y, fill=sail, outline="")
        canvas.create_rectangle(x + 6, y + 19, x + 17, y + 20, fill="#d1ecdf" if night else "#dff3df", outline="")
        canvas.create_rectangle(x + 29, y + 19, x + 39, y + 20, fill="#d1ecdf" if night else "#dff3df", outline="")

    def _draw_night_sky(self, canvas: tk.Canvas, width: int) -> None:
        moon_x = width - 105
        canvas.create_oval(moon_x - 25, 14, moon_x + 25, 64, fill="#f8e6a8", outline="")
        canvas.create_oval(moon_x - 12, 9, moon_x + 31, 52, fill="#182b45", outline="")
        stars = [(58, 23), (132, 18), (183, 48), (246, 27), (320, 18), (392, 47), (466, 25), (542, 17), (625, 49)]
        for x, y in stars:
            canvas.create_rectangle(x, y, x + 3, y + 3, fill="#fff4bd", outline="")
            canvas.create_rectangle(x - 2, y + 1, x + 5, y + 2, fill="#fff4bd", outline="")

    @staticmethod
    def _draw_media_on_grass(canvas: tk.Canvas, width: int, night: bool) -> None:
        """Draw scattered pixel-art CDs and DVDs in the foreground grass."""
        discs = [
            (48, 130, 12, "#d78c88"),
            (142, 141, 9, "#8cc9c1"),
            (238, 128, 13, "#d6b86d"),
            (344, 140, 10, "#a89bd0"),
            (452, 130, 11, "#83b9d2"),
            (566, 142, 13, "#d39b70"),
            (672, 129, 9, "#b8c987"),
        ]
        holo_colors = (
            ["#6c8992", "#8c7297", "#8d8c5c", "#668da1"]
            if night
            else ["#e9a7c6", "#76cfc4", "#f1d37c", "#a9a0df"]
        )
        for x, y, size, color in discs:
            if x > width - 4:
                continue
            rim = "#aab47a" if night else color
            canvas.create_oval(x, y, x + size, y + size * 0.62, fill=rim, outline="")
            # Iridescent holographic bands catch the light on each disc.
            for arc_index, start in enumerate((15, 135, 255)):
                canvas.create_arc(
                    x + 1,
                    y + 1,
                    x + size - 1,
                    y + size * 0.62 - 1,
                    start=start,
                    extent=62,
                    style=tk.ARC,
                    outline=holo_colors[(arc_index + int(x)) % len(holo_colors)],
                    width=1,
                )
            canvas.create_oval(
                x + size * 0.35,
                y + size * 0.18,
                x + size * 0.65,
                y + size * 0.44,
                fill="#31553e" if night else "#6f9d52",
                outline="",
            )
            canvas.create_rectangle(x + 2, y + 1, x + 4, y + 2, fill="#f8efbe" if not night else "#dce4af", outline="")

    def _is_night(self) -> bool:
        try:
            hour, minute = (int(part) for part in self.night_start_var.get().strip().split(":", 1))
            threshold = time(hour=hour, minute=minute)
        except (ValueError, TypeError):
            threshold = time(hour=20, minute=0)
        return datetime.now().time() >= threshold

    def _on_night_time_changed(self, *_args: str) -> None:
        if hasattr(self, "header_canvas"):
            self._draw_header()

    def _refresh_sky(self) -> None:
        if self.winfo_exists():
            self._draw_header()
            self.after(30_000, self._refresh_sky)

    @staticmethod
    def _cloud(canvas: tk.Canvas, x: int, y: int, sky: str) -> None:
        cloud = "#f7fbf1"
        canvas.create_rectangle(x, y + 10, x + 70, y + 25, fill=cloud, outline="")
        canvas.create_oval(x + 8, y, x + 35, y + 22, fill=cloud, outline="")
        canvas.create_oval(x + 27, y - 8, x + 57, y + 23, fill=cloud, outline="")
        canvas.create_oval(x + 48, y + 5, x + 74, y + 24, fill=cloud, outline="")
        canvas.create_rectangle(x + 13, y + 21, x + 67, y + 26, fill=sky, outline="")

    def _field_label(self, parent: tk.Widget, text: str) -> None:
        tk.Label(
            parent, text=text, bg=self.COLORS["cream"], fg=self.COLORS["muted"],
            font=("Courier New", 8, "bold"), anchor="w",
        ).pack(fill="x")

    def _build_progress_card(self, parent: tk.Widget) -> None:
        card = tk.Frame(
            parent, bg=self.COLORS["paper"], highlightbackground=self.COLORS["line"],
            highlightthickness=2, padx=18, pady=14,
        )
        card.pack(fill="x")
        top = tk.Frame(card, bg=self.COLORS["paper"])
        top.pack(fill="x")
        tk.Label(
            top, textvariable=self.status_var, bg=self.COLORS["paper"], fg=self.COLORS["brown_dark"],
            font=("Courier New", 10, "bold"), anchor="w",
        ).pack(side="left")
        tk.Label(
            top, textvariable=self.detail_var, bg=self.COLORS["paper"], fg=self.COLORS["muted"],
            font=("Courier New", 8), anchor="e",
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))
        ttk.Progressbar(
            card, variable=self.progress_var, maximum=100, style="Meadow.Horizontal.TProgressbar"
        ).pack(fill="x", pady=(12, 2))

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.folder_var.get(), title="Choose where to save videos")
        if selected:
            self.folder_var.set(selected)

    def open_folder(self) -> None:
        folder = Path(self.folder_var.get()).expanduser()
        if not folder.exists():
            messagebox.showinfo(APP_TITLE, "This folder does not exist yet. It will be created with the first download.")
            return
        try:
            import os
            os.startfile(folder)  # type: ignore[attr-defined]
        except OSError as error:
            messagebox.showerror(APP_TITLE, f"I could not open the folder:\n{error}")

    @staticmethod
    def open_ytdlp_link() -> None:
        webbrowser.open_new_tab("https://github.com/yt-dlp/yt-dlp")

    def start_download(self) -> None:
        if self.downloading:
            return
        url = self.url_var.get().strip()
        folder = Path(self.folder_var.get()).expanduser()
        if not url:
            messagebox.showwarning(APP_TITLE, "Paste the video link first.")
            self.url_entry.focus_set()
            return
        if not self.folder_var.get().strip():
            messagebox.showwarning(APP_TITLE, "Choose a folder where the video should be saved.")
            return

        self.downloading = True
        self.progress_var.set(0)
        self.status_var.set("Harvesting your video…")
        self.detail_var.set("Preparing")
        self.download_button.configure(state="disabled")
        self.folder_button.configure(state="disabled")
        threading.Thread(target=self._download_worker, args=(url, folder), daemon=True).start()

    def _download_worker(self, url: str, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        options = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": str(output_dir / "%(title)s [%(id)s]" / "%(title)s [%(id)s].%(ext)s"),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            self.queue.put(("done", output_dir))
        except UnsupportedError:
            self.queue.put(("error", "This site or URL type is not supported by yt-dlp."))
        except DownloadError as error:
            self.queue.put(("error", f"Download failed: {error}"))
        except OSError as error:
            self.queue.put(("error", f"I could not create the destination folder: {error}"))
        except Exception as error:  # noqa: BLE001 - keep unexpected errors from closing the GUI
            self.queue.put(("error", f"An unexpected error occurred: {error}"))

    def _progress_hook(self, data: dict[str, Any]) -> None:
        state = data.get("status")
        if state == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else 0
            speed = data.get("speed")
            eta = data.get("eta")
            speed_text = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "…"
            eta_text = f" · {eta}s remaining" if eta is not None else ""
            self.queue.put(("progress", (percent, f"{speed_text}{eta_text}")))
        elif state == "finished":
            self.queue.put(("progress", (100, "Finalizing…")))

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.queue.get_nowait()
                if event == "progress":
                    percent, detail = payload
                    self.progress_var.set(percent)
                    self.detail_var.set(detail)
                elif event == "done":
                    self.downloading = False
                    self.progress_var.set(100)
                    self.status_var.set("Harvest complete! ✦")
                    self.detail_var.set("Your video is safe in its folder")
                    self._set_controls_enabled(True)
                    messagebox.showinfo(APP_TITLE, f"Download complete!\n\nSaved to:\n{payload.resolve()}")
                elif event == "error":
                    self.downloading = False
                    self.status_var.set("The harvest did not succeed")
                    self.detail_var.set("Check the link and try again")
                    self._set_controls_enabled(True)
                    messagebox.showerror(APP_TITLE, payload)
        except queue.Empty:
            pass
        self.after(100, self._process_events)

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.download_button.configure(state=state)
        self.folder_button.configure(state=state)


if __name__ == "__main__":
    VideoMeadow().mainloop()
