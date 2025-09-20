# Leopold's Vault - Refactored GUI Application

## Overview

Leopold's Vault is a sophisticated movie download management application with a modern PyQt5 GUI. The application has been completely refactored for modularity, maintainability, and enhanced functionality.

## Architecture

### Modular Structure

The application is now organized into the following modules:

```
vault44/
├── gui_downloader.py       # Main application window
├── utilities.py            # Shared utility functions
├── tabs/                   # Tab modules directory
│   ├── __init__.py        # Package initialization
│   ├── activity_log_tab.py       # Activity logging and monitoring
│   ├── movie_list_tab.py          # Movie list management
│   ├── nextup_tab.py             # Next up movies queue
│   ├── torrent_tracker_tab.py    # Torrent monitoring and control
│   ├── settings_tab.py           # Application settings
│   └── recommendations_tab.py    # AI-powered movie recommendations
├── test_refactoring.py     # Comprehensive test suite
└── .gitignore             # Git ignore file
```

## Features

### 🎬 Activity Log Tab
- Real-time activity monitoring
- Color-coded log levels (INFO, SUCCESS, WARNING, ERROR)
- Separate download progress tracking
- Auto-scrolling log display
- Clear log functionality

### 📋 Movie List Tab
- Add/remove movies from download list
- Import movies from text files
- Duplicate detection
- Search and filter functionality
- Movie details preview
- Priority marking

### ⏭️ Next Up Tab
- Manage movies to watch next
- Play movie functionality
- Mark as watched
- Movie information display
- Search online integration

### 🌊 Torrent Tracker Tab
- Real-time torrent monitoring
- Pause/resume/remove controls
- Filter by status (All, Downloading, Paused, Completed, Error)
- Detailed torrent information
- Progress tracking with visual indicators
- qBittorrent integration

### ⚙️ Settings Tab
- Comprehensive application configuration
- Download path management
- qBittorrent connection settings
- Interface customization options
- Advanced debugging settings
- Test connection functionality

### 🎯 Recommendations Tab
- AI-powered movie recommendations
- Multiple recommendation algorithms:
  - Similar Genre
  - Popular movies
  - Recent releases
  - Director/Actor based
- Filter watched movies
- Add recommendations to download list
- Search and filter recommendations

## Installation

### Requirements

```bash
pip install PyQt5 psutil qbittorrent-api requests
```

### Dependencies

- **PyQt5**: GUI framework
- **psutil**: Process monitoring
- **qbittorrent-api**: qBittorrent client integration
- **requests**: HTTP requests

## Usage

### Running the Application

```bash
python gui_downloader.py
```

### Configuration

The application uses a `settings.json` file for configuration:

```json
{
  "save_path": "/path/to/downloads",
  "max_active_torrents": 3,
  "qb_host": "127.0.0.1",
  "qb_port": 8080,
  "qb_user": "admin",
  "qb_pass": "adminadmin",
  "theme": "Dark",
  "refresh_interval": 3,
  "show_notifications": true,
  "minimize_to_tray": false,
  "log_level": "INFO",
  "debug_mode": false
}
```

## Key Improvements

### 🏗️ Architecture
- **Modular Design**: Each tab is now a separate module
- **Separation of Concerns**: Utilities separated from GUI logic
- **Clean Imports**: Proper package structure with `__init__.py`
- **Maintainable Code**: Clear class hierarchy and organization

### 🎨 User Interface
- **Professional Styling**: Gradient backgrounds and consistent theming
- **Enhanced Widgets**: Progress bars, search fields, filter controls
- **Visual Feedback**: Color-coded status indicators
- **Responsive Layout**: Splitters and proper widget sizing

### 🔧 Functionality
- **Real-time Updates**: Timers for automatic refresh
- **Signal-Slot Communication**: Proper inter-component messaging
- **Error Handling**: Comprehensive exception handling
- **Data Persistence**: Settings and state management

### 🛠️ Developer Experience
- **Type Hints**: Improved code documentation
- **Docstrings**: Comprehensive documentation
- **Test Suite**: Validation of all modules
- **Git Integration**: Proper .gitignore and version control

## Testing

Run the comprehensive test suite:

```bash
python test_refactoring.py
```

The test suite validates:
- File structure integrity
- Module imports and dependencies
- Utility function correctness
- GUI class structure
- Cross-module communication

## API Reference

### Utilities Module

```python
from utilities import (
    load_settings,      # Load application settings
    save_settings,      # Save application settings
    read_file_lines,    # Read lines from file
    write_file_lines,   # Write lines to file
    parse_movie_title,  # Parse movie title and year
    format_file_size,   # Format file size for display
    launch_qbittorrent  # Launch qBittorrent client
)
```

### Tab Classes

```python
from tabs import (
    ActivityLogTab,      # Activity logging tab
    MovieListTab,        # Movie list management tab
    NextUpTab,          # Next up movies tab
    TorrentTrackerTab,  # Torrent monitoring tab
    SettingsTab,        # Application settings tab
    RecommendationsTab  # Movie recommendations tab
)
```

## Contributing

The modular structure makes contributing easier:

1. **Adding New Tabs**: Create new tab modules in the `tabs/` directory
2. **Extending Utilities**: Add functions to `utilities.py`
3. **UI Improvements**: Modify individual tab classes
4. **Testing**: Add tests to `test_refactoring.py`

## Future Enhancements

- [ ] Database integration for movie metadata
- [ ] Machine learning recommendations
- [ ] Plugin system for custom tabs
- [ ] Themes and customization
- [ ] Multi-language support
- [ ] Cloud synchronization

## License

This project is part of the vault44 repository by leopoldi44.

---

*Refactored with ❤️ for better modularity and maintainability*