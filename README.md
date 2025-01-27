# MP3 File Selector

A Python tool to organize and manage your MP3 files by creating custom selections based on artists and file size limits.

## Features

### MP3 Selector GUI (`mp3_selector_gui.py`)
- User-friendly graphical interface
- Select source and destination folders through file browser
- Configure all settings through the interface:
  - Maximum songs per artist
  - Total size limit
  - Copy mode (files or shortcuts)
- Real-time progress display
- Error handling with user notifications

### MP3 Selector (`mp3_selector.py`)
- Normalizes text and special characters in filenames
- Reads MP3 metadata (ID3 tags)
- Groups songs by artist
- Selects songs based on configurable rules:
  - Maximum number of songs per artist
  - Total size limit in GB
- Supports two output modes:
  - Copy files to destination folder
  - Create shortcuts (.lnk files)

### Playlist Creator (`create_playlist.py`)
- Resolves .lnk shortcuts to find original MP3 files
- Creates .m3u playlist files with correct file paths

## Installation & Usage

### Executable Version (Windows)
The easiest way to use the application is through the executable file:
1. Download the `mp3_selector_gui.exe` from the `dist` folder
2. Double-click to run - no installation or Python required
3. Use the graphical interface to select folders and configure settings

### Python Version
If you prefer to run from source, you'll need Python installed with these requirements:

```bash
pip install mutagen pywin32 tkinter
```

Then you can run either:

### GUI Version (Recommended)
1. Run the GUI version:
```bash
python mp3_selector_gui.py
```
2. Use the interface to:
   - Select folders
   - Configure settings
   - Start the selection process

### Command Line Version
1. Set up your configuration in the script
2. Run the MP3 selector:
```bash
python mp3_selector.py
```
3. To create a playlist from the selected files:
```bash
python create_playlist.py
```

## Configuration

Edit the following variables in the scripts to customize behavior (only needed for command line version):

```python
# in mp3_selector.py
ORIGIN_FOLDER = "path/to/your/music/folder"
DESTINATION_FOLDER = "path/to/output/folder"
MAX_SONGS_PER_ARTIST = 3
MAX_SIZE_GB = 10
CREATE_SHORTCUTS = True  # False to copy files instead
```

## How it Works

1. The script scans the origin folder for MP3 files
2. Reads metadata to group songs by artist
3. Randomly selects songs while respecting the configured limits
4. Either copies files or creates shortcuts in the destination folder
5. Optionally creates a playlist file with the selected songs

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
