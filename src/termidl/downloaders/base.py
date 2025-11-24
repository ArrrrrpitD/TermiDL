from abc import ABC, abstractmethod
from typing import Optional, Callable

class BaseDownloader(ABC):
    def __init__(self, download_path: str):
        self.download_path = download_path
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.status = "idle"  # idle, downloading, paused, completed, error, cancelled

    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """
        Set a callback function to receive progress updates.
        Callback signature: callback(percentage: float, status_message: str)
        """
        self.progress_callback = callback

    def _update_progress(self, percentage: float, message: str):
        if self.progress_callback:
            self.progress_callback(percentage, message)

    @abstractmethod
    async def download(self, url: str, filename: Optional[str] = None):
        """
        Start the download.
        """
        pass

    @abstractmethod
    def cancel(self):
        """
        Cancel the download.
        """
        pass
    
    @abstractmethod
    def pause(self):
        """
        Pause the download (if supported).
        """
        pass

    @abstractmethod
    def resume(self):
        """
        Resume the download (if supported).
        """
        pass
