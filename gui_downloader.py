import subprocess
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
    QTabWidget, QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QBrush, QColor

# Import utilities and tab classes
from utilities import (
    load_settings, save_settings, launch_qbittorrent, 
    read_file_lines, COLLECTION_FILE, PROCESSED_MOVIES_FILE, DOWNLOAD_LIST_FILE
)
from tabs import (
    ActivityLogTab, MovieListTab, NextUpTab, TorrentTrackerTab, 
    SettingsTab, RecommendationsTab
)

# qBittorrent connection constants
QB_HOST = "127.0.0.1"
QB_PORT = "8080"
QB_USER = "admin"
QB_PASS = "adminadmin"

class MainGUI(QWidget):
    """Main GUI window for Leopold's Vault."""
    
    direct_download_signal = pyqtSignal(str, int, int, str)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.init_settings()
        self.init_ui()
        self.setup_connections()
        
        # AUTO-LAUNCH QBittorrent on startup
        launch_qbittorrent()

    def init_settings(self):
        """Initialize application settings."""
        s = load_settings()
        self.save_path = s.get("save_path", r"C:\Users\leopold\Desktop\MOVIES (SSD)")
        self.movie_list_path = DOWNLOAD_LIST_FILE
        self.max_active_torrents = s.get("max_active_torrents", 3)
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Leopold's Vault")
        self.setGeometry(60, 60, 1150, 850)
        
        # Set up gradient background
        self.setAutoFillBackground(True)
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1000)
        gradient.setColorAt(0.0, QColor("#19191d"))
        gradient.setColorAt(0.4, QColor("#232335"))
        gradient.setColorAt(1.0, QColor("#181824"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Leopold's Vault")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; letter-spacing:2px; margin:14px; text-shadow: 2px 2px #000;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Load data
        self.collection = read_file_lines(COLLECTION_FILE)
        self.processed = read_file_lines(PROCESSED_MOVIES_FILE)
        self.planned = read_file_lines(DOWNLOAD_LIST_FILE)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.create_tabs()
        main_layout.addWidget(self.tabs)
        
        # Bottom controls
        bottom_layout = self.create_bottom_controls()
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
        
    def create_tabs(self):
        """Create all tabs."""
        # Activity Log Tab
        self.activity_tab = ActivityLogTab()
        self.tabs.addTab(self.activity_tab, "Activity Log")
        
        # Movie List Tab
        self.list_tab = MovieListTab(self.movie_list_path)
        self.tabs.addTab(self.list_tab, "Movie List")
        
        # Next Up Tab
        self.nextup_tab = NextUpTab(self.planned, play_callback=self.play_nextup)
        self.tabs.addTab(self.nextup_tab, "Next Up")
        
        # Recommendations Tab
        self.recommend_tab = RecommendationsTab(self.processed, self.collection, self)
        self.tabs.addTab(self.recommend_tab, "Recommendations")
        
        # Torrent Tracker Tab
        self.torrent_tab = TorrentTrackerTab(self)
        self.tabs.addTab(self.torrent_tab, "Torrent Tracker")
        
        # Settings Tab
        self.settings_tab = SettingsTab(self)
        self.tabs.addTab(self.settings_tab, "Settings")
        
    def create_bottom_controls(self):
        """Create bottom control panel."""
        bottom_layout = QHBoxLayout()
        
        # Save folder display and button
        self.folder_label = QLabel(f"Save Folder: {self.save_path}")
        self.folder_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.folder_label.setStyleSheet("color: #e9d8a6; background: transparent;")
        bottom_layout.addWidget(self.folder_label)
        
        folder_btn = QPushButton("Select Folder")
        folder_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        folder_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 11px;
                padding: 8px 19px;
                font-weight: 700;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        folder_btn.clicked.connect(self.select_folder)
        bottom_layout.addWidget(folder_btn)
        
        # Download control buttons
        self.start_btn = QPushButton("Start Download")
        self.start_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                color: #232330;
                background: #e9d8a6;
                border-radius: 11px;
                padding: 8px 30px;
                font-weight: 700;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #fffbe6;
            }
        """)
        self.start_btn.clicked.connect(self.start_download)
        
        self.stop_btn = QPushButton("Stop Download")
        self.stop_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                color: #fffbe6;
                background: #b82121;
                border-radius: 11px;
                padding: 8px 30px;
                font-weight: 700;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #ff3b3b;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        return bottom_layout
        
    def setup_connections(self):
        """Setup signal connections between components."""
        # Tab change handler
        self.tabs.currentChanged.connect(self.tab_changed)
        
        # Movie list tab connections
        if hasattr(self.list_tab, 'movie_added'):
            self.list_tab.movie_added.connect(self.on_movie_added)
        if hasattr(self.list_tab, 'movie_removed'):
            self.list_tab.movie_removed.connect(self.on_movie_removed)
            
        # Recommendations tab connections
        if hasattr(self.recommend_tab, 'add_to_list_requested'):
            self.recommend_tab.add_to_list_requested.connect(self.add_movie_to_list)
            
        # Settings tab connections
        if hasattr(self.settings_tab, 'settings_changed'):
            self.settings_tab.settings_changed.connect(self.on_settings_changed)
            
    def select_folder(self):
        """Select download folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.save_path)
        if folder:
            self.save_path = folder
            self.folder_label.setText(f"Save Folder: {self.save_path}")
            
            # Update settings
            settings = load_settings()
            settings["save_path"] = self.save_path
            save_settings(settings)
            
    def start_download(self):
        """Start the download process."""
        if self.process and self.process.poll() is None:
            QMessageBox.warning(self, "Warning", "Download process is already running!")
            return
            
        try:
            self.process = subprocess.Popen([
                sys.executable, "movie_downloader2.py"
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            # Log the action
            if hasattr(self.activity_tab, 'add_log_entry'):
                self.activity_tab.add_log_entry("Download process started", "SUCCESS")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start download process:\n{str(e)}")
            if hasattr(self.activity_tab, 'add_log_entry'):
                self.activity_tab.add_log_entry(f"Failed to start download: {str(e)}", "ERROR")
                
    def stop_download(self):
        """Stop the download process."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Log the action
        if hasattr(self.activity_tab, 'add_log_entry'):
            self.activity_tab.add_log_entry("Download process stopped", "WARNING")
            
    def tab_changed(self, index):
        """Handle tab change."""
        tab_names = ["Activity Log", "Movie List", "Next Up", "Recommendations", "Torrent Tracker", "Settings"]
        if 0 <= index < len(tab_names):
            if hasattr(self.activity_tab, 'add_log_entry'):
                self.activity_tab.add_log_entry(f"Switched to {tab_names[index]} tab", "INFO")
                
    def play_nextup(self, movie_text):
        """Play callback for next up tab."""
        # In a real implementation, this would launch a media player
        if hasattr(self.activity_tab, 'add_log_entry'):
            self.activity_tab.add_log_entry(f"Playing movie: {movie_text}", "INFO")
        print(f"Playing: {movie_text}")
        
    def on_movie_added(self, movie_text):
        """Handle movie added to list."""
        if hasattr(self.activity_tab, 'add_log_entry'):
            self.activity_tab.add_log_entry(f"Added movie to list: {movie_text}", "SUCCESS")
            
    def on_movie_removed(self, movie_text):
        """Handle movie removed from list."""
        if hasattr(self.activity_tab, 'add_log_entry'):
            self.activity_tab.add_log_entry(f"Removed movie from list: {movie_text}", "WARNING")
            
    def add_movie_to_list(self, movie_text):
        """Add movie to download list from recommendations."""
        if hasattr(self.list_tab, 'movie_input') and hasattr(self.list_tab, 'add_movie'):
            self.list_tab.movie_input.setText(movie_text)
            self.list_tab.add_movie()
            
            # Switch to movie list tab
            self.tabs.setCurrentWidget(self.list_tab)
            
    def on_settings_changed(self, new_settings):
        """Handle settings change."""
        self.save_path = new_settings.get("save_path", self.save_path)
        self.max_active_torrents = new_settings.get("max_active_torrents", self.max_active_torrents)
        
        if hasattr(self.activity_tab, 'add_log_entry'):
            self.activity_tab.add_log_entry("Settings updated", "INFO")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())
