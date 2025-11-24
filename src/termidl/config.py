import json
import os
from pathlib import Path
from typing import Any, Dict

CONFIG_FILE = Path.home() / ".termidl_config.json"

DEFAULT_CONFIG = {
    "download_path": str(Path.home() / "Downloads"),
    "max_concurrent_downloads": 3,
    "theme": "default",
    "aria2_path": "aria2c",
    "ytdlp_path": "yt-dlp"
}

class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, "r") as f:
                user_config = json.load(f)
                # Merge with default to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str) -> Any:
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()
