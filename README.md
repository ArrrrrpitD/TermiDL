# TermiDL

> **A Modern Terminal-Based Download Manager**

**TermiDL** is a powerful, terminal-based download manager with a rich Textual User Interface (TUI). It unifies downloading from torrents, direct links, and YouTube into a single, easy-to-use application.

```
 _____                   _  ______ _     
|_   _|                 (_) |  _  \ |    
  | | ___ _ __ _ __ ___  _  | | | | |    
  | |/ _ \ '__| '_ ` _ \| | | | | | |    
  | |  __/ |  | | | | | | | | |/ /| |____
  \_/\___|_|  |_| |_| |_|_| |___/ \_____/
```                                       
                                         

## ✨ Features

- **🖥️ Modern TUI**: Built with [Textual](https://textual.textualize.io/), featuring mouse support, dashboards, and real-time progress bars.
- **🚀 Universal Downloader**:
  - **Torrents & Magnet Links**: Powered by `aria2`.
  - **YouTube & Playlists**: Powered by `yt-dlp`.
  - **Direct Downloads**: High-speed HTTP/HTTPS downloads.
- **⚙️ Configurable**: Automatically saves your download paths and preferences.
- **📦 Modular**: Clean Python package structure.

## 🛠️ Requirements

- **Python 3.8+**
- **aria2**: Must be installed and in your system PATH.
  - *Windows*: `winget install aria2` or download from [aria2.github.io](https://aria2.github.io/)
  - *Linux*: `sudo apt install aria2`
- **FFmpeg**: Required for some YouTube downloads.

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arpitdwivedi1185/TermiDL.git
   cd TermiDL
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

## 🚀 Usage

Run the application:

```bash
termidl
```

Or via python:

```bash
python -m termidl
```

### Controls
- **`a`**: Add a new download.
- **`q`**: Quit the application.
- **Mouse**: You can click buttons and interact with the UI using your mouse!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
