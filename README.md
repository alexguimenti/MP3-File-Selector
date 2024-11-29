# MP3 File Selector and Organizer

This Python script selects and copies (or creates shortcuts) for MP3 files from a source folder to a destination folder based on specific rules and limitations.

## Features

- **Normalize Text**: Removes accents and converts text to lowercase.
- **Read Metadata**: Extracts artist and title information from MP3 files.
- **List MP3 Files**: Lists MP3 files in a specified folder and extracts their metadata.
- **Group by Artist**: Groups songs by artist.
- **Select Songs**: Selects songs based on the number of songs per artist.
- **Limit Songs by Size**: Limits the selection of songs based on a maximum size in GB.
- **Copy or Create Shortcuts**: Copies selected songs or creates shortcuts (.lnk files) in the destination folder.

## Configuration

You can configure the script by modifying the following parameters:

- `music_folder`: Path to the folder containing the MP3 files.
- `destination_folder`: Path to the destination folder where the selected files or shortcuts will be placed.
- `test_limit`: Limit of files for the initial test (default is 999999).
- `songs_per_artist`: Number of songs to select per artist in Group 1 (default is 5).
- `max_size_gb`: Maximum total size of files to copy or link, in GB (default is 5).
- `copy_mode`: If `True`, copy files; if `False`, create Windows shortcuts (.lnk).

## How to Use

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/mp3-file-selector.git
    cd mp3-file-selector
    ```

2. **Install Dependencies**:
    Make sure you have the required dependencies installed. You can install them using pip:
    ```sh
    pip install mutagen pywin32
    ```

3. **Configure the Script**:
    Edit the script to set the paths and configuration parameters according to your needs:
    ```python
    music_folder = r"D:\Backup"
    destination_folder = r"C:\Users\alexg\Music\Temp"
    test_limit = 999999
    songs_per_artist = 5
    max_size_gb = 5
    copy_mode = False
    ```

4. **Run the Script**:
    Execute the script using Python:
    ```sh
    python mp3_selector.py
    ```

## Script Overview

### Functions

- **normalize_text(text)**:
    Normalizes text by removing accents and converting to lowercase.

- **read_metadata(file_path)**:
    Reads metadata (artist and title) from an MP3 file.

- **list_mp3_files(folder, limit=None)**:
    Lists MP3 files in a specified folder and extracts their metadata.

- **group_by_artist(songs)**:
    Groups songs by artist.

- **select_songs_based_on_artist_count(groups_by_artist, songs_per_artist)**:
    Selects songs based on the number of songs per artist.

- **limit_songs_by_size(selected_songs, max_size_bytes)**:
    Limits the selection of songs based on a maximum size in bytes.

- **normalize_path(path)**:
    Removes special characters from the path.

- **copy_or_link_selected_songs(selected_songs, destination, copy_mode=True)**:
    Copies selected songs or creates shortcuts (.lnk files) in the destination folder.

