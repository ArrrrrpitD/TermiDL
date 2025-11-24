import asyncio
import re
import os
from .base import BaseDownloader

class Aria2Downloader(BaseDownloader):
    def __init__(self, download_path: str):
        super().__init__(download_path)
        self.process = None
        self.loop = asyncio.get_event_loop()

    async def download(self, url: str, filename: str = None):
        self.status = "downloading"
        self._update_progress(0, "Starting download...")

        # Resolve filename if not provided
        if not filename:
            filename = await self.loop.run_in_executor(None, self._resolve_filename, url)
        
        self.name = filename
        
        # Build command
        cmd = ["aria2c", "--dir", self.download_path, "--seed-time=0", "--summary-interval=1"]
        
        # Explicitly set output filename to ensure we know what it is
        cmd.extend(["--out", self.name])
        
        cmd.append(url)

        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Regex to parse aria2 output
            # Example: [#2089b0 400.0KiB/33.0MiB(1%) CN:1 DL:115.0KiB ETA:4m51s]
            # Permissive regex for ETA
            progress_pattern = re.compile(r"\((\d+)%\).*DL:([\w.]+).*ETA:([^\s\]]*)")
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

            while True:
                line = await self.process.stdout.readline()
                if not line:
                    break
                
                # Strip ANSI codes for easier parsing
                decoded_line = ansi_escape.sub('', line.decode().strip())
                
                match = progress_pattern.search(decoded_line)
                if match:
                    percent = float(match.group(1))
                    speed = match.group(2)
                    eta = match.group(3)
                    if not eta:
                        eta = "Unknown"
                    self._update_progress(percent, f"Speed: {speed} | ETA: {eta}")
                
            await self.process.wait()

            if self.status == "cancelled":
                self._update_progress(0, "Cancelled")
                return

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

    def _resolve_filename(self, url: str) -> str:
        import urllib.request
        import urllib.parse
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers, method='HEAD')
            with urllib.request.urlopen(req) as response:
                cd = response.getheader('Content-Disposition')
                if cd:
                    fname = re.findall(r'filename="?([^"]+)"?', cd)
                    if fname:
                        return fname[0]
                final_url = response.geturl()
                path = urllib.parse.urlparse(final_url).path
                return os.path.basename(path) or "download"
        except:
            return os.path.basename(urllib.parse.urlparse(url).path) or "download"

    def cancel(self):
        if self.process:
            self.process.terminate()
            self.status = "cancelled"
            self._update_progress(0, "Cancelled")
            
            # Cleanup files
            try:
                if self.name and self.name != "Unknown":
                    file_path = os.path.join(self.download_path, self.name)
                    aria2_path = file_path + ".aria2"
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if os.path.exists(aria2_path):
                        os.remove(aria2_path)
            except Exception as e:
                print(f"Cleanup failed: {e}")

    def pause(self):
        # Aria2c subprocess cannot be easily paused without RPC
        pass

    def resume(self):
        pass
