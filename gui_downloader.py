import subprocess
import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
    QListWidget, QListWidgetItem, QTabWidget, QLineEdit, QSpinBox, QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QBrush, QColor

# ... your helper imports and code ...

QB_HOST = "127.0.0.1"
QB_PORT = "8080"
QB_USER = "admin"
QB_PASS = "adminadmin"

def launch_qbittorrent():
    """Auto-launch qBittorrent client if not running."""
    import platform
    import psutil

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

class TorrentTrackerTab(QWidget):
    # ... unchanged except for improved error handling if desired ...
    # (Keep pause/resume/remove logic as before)

    # [see previous semantic search blocks for implementation]

class SettingsTab(QWidget):
    # ... unchanged ...

class MainGUI(QWidget):
    direct_download_signal = pyqtSignal(str, int, int, str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leopold's Vault")
        self.setGeometry(60, 60, 1150, 850)
        s = load_settings()
        self.save_path = s.get("save_path", r"C:\Users\leopold\Desktop\MOVIES (SSD)")
        self.movie_list_path = DOWNLOAD_LIST_FILE
        self.max_active_torrents = s.get("max_active_torrents", 3)
        self.setAutoFillBackground(True)
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1000)
        gradient.setColorAt(0.0, QColor("#19191d"))
        gradient.setColorAt(0.4, QColor("#232335"))
        gradient.setColorAt(1.0, QColor("#181824"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        title = QLabel("Leopold's Vault")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; letter-spacing:2px; margin:14px; text-shadow: 2px 2px #000;")
        title.setAlignment(Qt.AlignCenter)
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        self.collection = read_file_lines(COLLECTION_FILE)
        self.processed = read_file_lines(PROCESSED_MOVIES_FILE)
        self.planned = read_file_lines(DOWNLOAD_LIST_FILE)
        self.tabs = QTabWidget()
        self.activity_tab = ActivityLogTab()
        self.list_tab = MovieListTab(self.movie_list_path)
        self.nextup_tab = NextUpTab(self.planned, play_callback=self.play_nextup)
        self.recommend_tab = RecommendationsTab(self.processed, self.collection, self)
        self.torrent_tab = TorrentTrackerTab(self)
        self.settings_tab = SettingsTab(self)
        self.settings_tab.gui = self
        self.tabs.addTab(self.activity_tab, "Activity Log")
        self.tabs.addTab(self.list_tab, "Movie List")
        self.tabs.addTab(self.nextup_tab, "Next Up")
        self.tabs.addTab(self.recommend_tab, "Recommendations")
        self.tabs.addTab(self.torrent_tab, "Torrent Tracker")
        self.tabs.addTab(self.settings_tab, "Settings")
        main_layout.addWidget(self.tabs)
        bottom_layout = QHBoxLayout()
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
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.process = None
        self.tabs.currentChanged.connect(self.tab_changed)
        # AUTO-LAUNCH QBittorrent on startup
        launch_qbittorrent()

    # ... rest of the MainGUI methods as before ...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())
