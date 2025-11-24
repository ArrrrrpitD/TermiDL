import asyncio
import re
import os
from .base import BaseDownloader

class Aria2Downloader(BaseDownloader):
    def __init__(self, download_path: str):
        super().__init__(download_path)
        self.process = None

    async def download(self, url: str, filename: str = None):
        self.status = "downloading"
        self._update_progress(0, "Starting download...")

        # Build command
        cmd = ["aria2c", "--dir", self.download_path, "--seed-time=0", "--summary-interval=1"]
        
        if filename:
            cmd.extend(["--out", filename])
        
        cmd.append(url)

        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Regex to parse aria2 output
            # Example: [#2089b0 400.0KiB/33.0MiB(1%) CN:1 DL:115.0KiB ETA:4m51s]
            progress_pattern = re.compile(r"\((\d+)%\).*DL:([\w.]+) ETA:([\w\d]+)")

            while True:
                line = await self.process.stdout.readline()
                if not line:
                    break
                
                decoded_line = line.decode().strip()
                match = progress_pattern.search(decoded_line)
                if match:
                    percent = float(match.group(1))
                    speed = match.group(2)
                    eta = match.group(3)
                    self._update_progress(percent, f"Speed: {speed} | ETA: {eta}")

            await self.process.wait()

            if self.process.returncode == 0:
                self.status = "completed"
                self._update_progress(100, "Download completed!")
            else:
                self.status = "error"
                stderr = await self.process.stderr.read()
                self._update_progress(0, f"Error: {stderr.decode().strip()}")

        except Exception as e:
            self.status = "error"
            self._update_progress(0, f"Exception: {str(e)}")

    def cancel(self):
        if self.process:
            self.process.terminate()
            self.status = "cancelled"
            self._update_progress(0, "Cancelled")

    def pause(self):
        # Aria2c subprocess cannot be easily paused without RPC
        pass

    def resume(self):
        pass
