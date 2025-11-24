from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, DataTable, Input, Label, Select, Static
from textual.widgets.data_table import RowDoesNotExist
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import work
import asyncio
import os

from termidl.config import ConfigManager
from termidl.downloaders.aria2 import Aria2Downloader
from termidl.downloaders.ytdlp import YtDlpDownloader

class AddDownloadScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Add New Download", id="title"),
            Input(placeholder="URL / Magnet Link", id="url"),
            Input(placeholder="Destination Path", value=self.app.config_manager.get("download_path"), id="path"),
            Select([("Direct/Torrent (Aria2)", "aria2"), ("YouTube (yt-dlp)", "ytdlp")], prompt="Select Type", id="type"),
            Horizontal(
                Button("Download", variant="primary", id="download"),
                Button("Cancel", variant="error", id="cancel"),
                classes="buttons"
            ),
            id="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
        elif event.button.id == "download":
            url = self.query_one("#url", Input).value
            path = self.query_one("#path", Input).value
            dl_type = self.query_one("#type", Select).value
            if url and path and dl_type:
                self.dismiss((url, path, dl_type))

class TermiDLApp(App):
    CSS = """
    #dialog {
        background: $surface;
        padding: 2;
        border: solid $primary;
        width: 60;
        height: auto;
        align: center middle;
    }
    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        text-style: bold;
    }
    .buttons {
        align: center middle;
        margin-top: 1;
    }
    Button {
        margin: 0 1;
    }
    DataTable {
        height: 1fr;
        border: solid $secondary;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_download", "Add Download"),
        Binding("c", "cancel_download", "Cancel Download"),
        Binding("delete", "cancel_download", "Cancel Download"),
    ]

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.downloads = {} # id -> downloader instance
        self.download_counter = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("ID", key="ID")
        table.add_column("Type", key="Type")
        table.add_column("Name", key="Name")
        table.add_column("Status", key="Status")
        table.add_column("Progress", key="Progress")
        table.add_column("Details", width=40, key="Details")
        self.set_interval(0.5, self.update_table)

    def action_add_download(self) -> None:
        def check_add(result):
            if result:
                url, path, dl_type = result
                self.start_download(url, path, dl_type)

        self.push_screen(AddDownloadScreen(), check_add)

    def action_cancel_download(self) -> None:
        table = self.query_one(DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            dl_id = int(row_key.value)
            if dl_id in self.downloads:
                self.downloads[dl_id]["downloader"].cancel()
                self.downloads[dl_id]["status"] = "Cancelling..."
                self.notify(f"Cancelled download {dl_id}")
                self.update_table()
        except Exception as e:
            self.notify(f"Failed to cancel: {e}", severity="error")

    @work(exclusive=False)
    async def start_download(self, url: str, path: str, dl_type: str):
        self.download_counter += 1
        dl_id = self.download_counter
        
        if dl_type == "aria2":
            downloader = Aria2Downloader(path)
        else:
            downloader = YtDlpDownloader(path)
            
        self.downloads[dl_id] = {
            "downloader": downloader,
            "url": url,
            "type": dl_type,
            "progress": 0,
            "status": "Starting",
            "details": "",
            "name": "Unknown"
        }

        # Callback to update state
        def progress_cb(percent, msg, name):
            if dl_id in self.downloads:
                self.downloads[dl_id]["progress"] = percent
                self.downloads[dl_id]["details"] = msg
                self.downloads[dl_id]["status"] = downloader.status
                self.downloads[dl_id]["name"] = name

        downloader.set_progress_callback(progress_cb)
        
        # Start download
        await downloader.download(url)

    def update_table(self) -> None:
        table = self.query_one(DataTable)
        # Clear is expensive, better to update rows, but for MVP clear/add is okay or use keys
        # Using keys:
        for dl_id, data in self.downloads.items():
            row_key = str(dl_id)
            status = data["status"]
            progress = f"{data['progress']:.1f}%"
            details = data["details"]
            dl_type = data["type"]
            name = data["name"]
            
            try:
                table.get_row_index(row_key)
                table.update_cell(row_key, "Name", name)
                table.update_cell(row_key, "Status", status)
                table.update_cell(row_key, "Progress", progress)
                table.update_cell(row_key, "Details", details)
            except RowDoesNotExist:
                table.add_row(str(dl_id), dl_type, name, status, progress, details, key=row_key)

if __name__ == "__main__":
    app = TermiDLApp()
    app.run()
