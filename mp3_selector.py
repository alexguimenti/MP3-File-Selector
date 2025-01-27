import os
import random
import shutil
import unicodedata
from mutagen.easyid3 import EasyID3
from collections import defaultdict
import pythoncom
import win32com.client

# Define the path to the folder with MP3 files
music_folder = r"D:\Backup"
destination_folder = r"C:\Users\alexg\Music\Temp3"

# Configuration
test_limit = 999999  # Limit of files for the initial test (modifiable)
songs_per_artist = 3  # Number of songs to select per artist in Group 1
max_size_gb = 7  # Maximum total size of files to copy or link, in GB
copy_mode = True  # If True, copy files; if False, create Windows shortcuts (.lnk)

# Convert max size in GB to bytes for comparison
max_size_bytes = max_size_gb * (1024 ** 3)

# Function to normalize text (remove accents and convert to lowercase)
def normalize_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.lower()

# Function to read metadata of an MP3 file
def read_metadata(file_path):
    try:
        metadata = EasyID3(file_path)
        artist = metadata.get("artist", ["Unknown"])[0]
        title = metadata.get("title", ["Untitled"])[0]
        artist = normalize_text(artist)
        return {"path": file_path, "artist": artist, "title": title}
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Function to list MP3 files and extract metadata
def list_mp3_files(folder, limit=None):
    print("Starting to list MP3 files...")
    songs = []
    counter = 0
    current_folder = None

    for root, dirs, files in os.walk(folder):
        if root != current_folder:
            print(f"Processing folder: {root}")
            current_folder = root

        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                song = read_metadata(file_path)
                if song:
                    songs.append(song)
                    counter += 1

                if limit and counter >= limit:
                    print(f"Reached the limit of {limit} files.")
                    return songs

    print(f"Completed listing MP3 files. Total MP3 files found: {len(songs)}")
    return songs

# Function to group songs by "Artist"
def group_by_artist(songs):
    print("Grouping songs by artist...")
    groups = defaultdict(list)
    for song in songs:
        artist = song["artist"]
        groups[artist].append(song)
    print("Completed grouping by artist.")
    return groups

# Function to handle selection logic based on the number of songs per artist
def select_songs_based_on_artist_count(groups_by_artist, songs_per_artist):
    print("Selecting songs based on artist count...")
    selected_songs = []

    # Separate artists into two groups
    group_1 = {artist: songs for artist, songs in groups_by_artist.items() if len(songs) >= 6}
    group_2 = {artist: songs for artist, songs in groups_by_artist.items() if len(songs) <= 5}

    # For Group 1, select `songs_per_artist` songs per artist
    for artist, songs in group_1.items():
        selected_songs.extend(random.sample(songs, songs_per_artist))

    # Calculate 10% of the total songs selected from Group 1
    total_group_1_songs = len(selected_songs)
    group_2_selection_count = max(1, int(total_group_1_songs * 0.1))

    # Randomly select `group_2_selection_count` songs from Group 2 artists
    group_2_songs = [song for songs in group_2.values() for song in songs]
    selected_songs.extend(random.sample(group_2_songs, min(group_2_selection_count, len(group_2_songs))))

    print(f"Total songs selected: {len(selected_songs)} (Group 1: {total_group_1_songs}, Group 2: {group_2_selection_count})")
    return selected_songs

# Function to limit songs based on the maximum size in bytes
def limit_songs_by_size(selected_songs, max_size_bytes):
    print(f"Limiting total size of selected songs to {max_size_gb} GB...")
    limited_songs = []
    current_size = 0

    # Shuffle the selected songs to randomize the order
    random.shuffle(selected_songs)

    for song in selected_songs:
        file_size = os.path.getsize(song["path"])
        if current_size + file_size <= max_size_bytes:
            limited_songs.append(song)
            current_size += file_size
        else:
            break  # Stop adding songs if the limit is reached

    print(f"Total size of limited selection: {current_size / (1024 ** 3):.2f} GB with {len(limited_songs)} songs.")
    return limited_songs

# Helper function to remove special characters from the path
def normalize_path(path):
    return unicodedata.normalize('NFKD', path).encode('ASCII', 'ignore').decode('ASCII')

# Function to copy or create shortcuts (.lnk files) for selected songs
def copy_or_link_selected_songs(selected_songs, destination, copy_mode=True):
    if copy_mode:
        print("Copying selected songs to the destination folder...")
    else:
        print("Creating shortcuts for selected songs in the destination folder...")

    if not os.path.exists(destination):
        os.makedirs(destination)

    for i, song in enumerate(selected_songs, start=1):
        source_path = song["path"]
        file_name = os.path.basename(source_path)
        destination_path = os.path.join(destination, file_name)

        try:
            if copy_mode:
                shutil.copy2(source_path, destination_path)
            else:
                # Normalize path to handle special characters
                source_path_normalized = normalize_path(source_path)
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(destination_path + ".lnk")
                shortcut.TargetPath = source_path_normalized
                shortcut.Save()

            if i % 10 == 0:
                print(f"{i} songs processed...")
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")

    print("Completed processing songs.")

# Execute the program
print("Starting the song selection program...")
songs = list_mp3_files(music_folder, limit=test_limit)

if songs:
    print(f"Total MP3 files found: {len(songs)}")
    groups_by_artist = group_by_artist(songs)
    selected_songs = select_songs_based_on_artist_count(groups_by_artist, songs_per_artist)
    
    # If in copy mode, limit by size; otherwise, proceed without size limitation
    if copy_mode:
        limited_songs = limit_songs_by_size(selected_songs, max_size_bytes)
    else:
        limited_songs = selected_songs  # Ignore size limitation for shortcut creation
    
    if limited_songs:
        copy_or_link_selected_songs(limited_songs, destination_folder, copy_mode=copy_mode)
    else:
        print("No songs selected within the size limit. Exiting program.")
else:
    print("No MP3 files found in the specified folder.")

print("Program completed successfully.")

