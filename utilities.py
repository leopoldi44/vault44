"""
Utility functions for the vault44 GUI application.
"""
import os
import json
import subprocess
import platform
import psutil


# File paths constants
COLLECTION_FILE = "leo_movie_collection.csv"
PROCESSED_MOVIES_FILE = "processed_movies.txt"
DOWNLOAD_LIST_FILE = "movie_list.txt"
SETTINGS_FILE = "settings.json"


def read_file_lines(filepath):
    """Read lines from a file, return empty list if file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []


def write_file_lines(filepath, lines):
    """Write lines to a file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False


def load_settings():
    """Load application settings from JSON file."""
    default_settings = {
        "save_path": "downloads",
        "max_active_torrents": 3
    }
    
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # Merge with defaults to ensure all keys exist
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
            return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return default_settings


def save_settings(settings):
    """Save application settings to JSON file."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def launch_qbittorrent():
    """Auto-launch qBittorrent client if not running."""
    qb_proc_name = "qbittorrent.exe" if platform.system() == "Windows" else "qbittorrent"
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and qb_proc_name.lower() in proc.info['name'].lower():
            print("[+] qBittorrent is already running.", flush=True)
            return
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["qbittorrent"], shell=True)
        else:
            subprocess.Popen(["qbittorrent"])
        print("[+] Launched qBittorrent client.", flush=True)
    except Exception as e:
        print(f"[!] Failed to launch qBittorrent: {e}", flush=True)


def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


def parse_movie_title(line):
    """Parse movie title and year from a line."""
    line = line.strip()
    if not line:
        return None, None
    
    # Try to extract year from the end
    parts = line.split(',')
    if len(parts) >= 2:
        title = ','.join(parts[:-1]).strip()
        year = parts[-1].strip()
        try:
            year = int(year)
            return title, year
        except ValueError:
            pass
    
    # If no year found, treat whole line as title
    return line, None