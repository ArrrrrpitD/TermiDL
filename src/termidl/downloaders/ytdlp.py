import asyncio
import yt_dlp
import os
from .base import BaseDownloader

class YtDlpDownloader(BaseDownloader):
    def __init__(self, download_path: str):
        super().__init__(download_path)
        self.loop = asyncio.get_event_loop()
        self._cancel_requested = False

    async def download(self, url: str, filename: str = None):
        self.status = "downloading"
        self._update_progress(0, "Starting download...")
        self._cancel_requested = False

        ydl_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'noprogress': True
        }

        try:
            # Run blocking yt_dlp in a separate thread
            await self.loop.run_in_executor(None, self._run_yt_dlp, ydl_opts, url)
            
            if not self._cancel_requested:
                self.status = "completed"
                self._update_progress(100, "Download completed!")
            else:
                self.status = "cancelled"
                self._update_progress(0, "Cancelled")

        except Exception as e:
            self.status = "error"
            self._update_progress(0, f"Error: {str(e)}")

    def _run_yt_dlp(self, opts, url):
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def _progress_hook(self, d):
        if self._cancel_requested:
            raise Exception("Download cancelled")

        if d['status'] == 'downloading':
            try:
                # Update name if available
                if 'filename' in d:
                    # Try to get clean filename or title
                    self.name = os.path.basename(d['filename'])
                
                p = d.get('_percent_str', '0%').replace('%','')
                percent = float(p)
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                self._update_progress(percent, f"Speed: {speed} | ETA: {eta}")
            except:
                pass
        elif d['status'] == 'finished':
            self._update_progress(100, "Processing...")

    def cancel(self):
        self._cancel_requested = True
        # Note: yt_dlp doesn't have a clean way to stop mid-download from another thread 
        # without raising an exception in the hook.

    def pause(self):
        pass

    def resume(self):
        pass
