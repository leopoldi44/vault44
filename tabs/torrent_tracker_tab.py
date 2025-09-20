"""
Torrent Tracker Tab for monitoring and managing torrents.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QProgressBar, QHeaderView, QAbstractItemView,
    QSplitter, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
import qbittorrentapi
from utilities import format_file_size


class TorrentTrackerTab(QWidget):
    """Tab for monitoring and managing torrent downloads."""
    
    torrent_status_changed = pyqtSignal(str, str)  # hash, new_status
    
    def __init__(self, main_gui):
        super().__init__()
        self.main_gui = main_gui
        self.qb_client = None
        self.torrents_data = []
        self.init_ui()
        self.setup_timer()
        self.connect_qbittorrent()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Title and connection status
        header_layout = QHBoxLayout()
        
        title = QLabel("Torrent Tracker")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; margin: 10px;")
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #f38ba8; margin: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        main_layout.addLayout(header_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        refresh_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 8px;
                padding: 8px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_torrents)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.pause_btn.setStyleSheet("""
            QPushButton {
                color: #fffbe6;
                background: #f9e2af;
                border-radius: 8px;
                padding: 8px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #f9f2cf;
            }
        """)
        self.pause_btn.clicked.connect(self.pause_selected)
        self.pause_btn.setEnabled(False)
        
        self.resume_btn = QPushButton("▶ Resume")
        self.resume_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.resume_btn.setStyleSheet("""
            QPushButton {
                color: #232330;
                background: #a6e3a1;
                border-radius: 8px;
                padding: 8px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #a6f3a1;
            }
        """)
        self.resume_btn.clicked.connect(self.resume_selected)
        self.resume_btn.setEnabled(False)
        
        self.remove_btn = QPushButton("🗑 Remove")
        self.remove_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.remove_btn.setStyleSheet("""
            QPushButton {
                color: #fffbe6;
                background: #f38ba8;
                border-radius: 8px;
                padding: 8px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #ff6b9d;
            }
        """)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.remove_btn.setEnabled(False)
        
        # Filter combo
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("color: #e9d8a6;")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Downloading", "Paused", "Completed", "Error"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_torrents)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.resume_btn)
        controls_layout.addWidget(self.remove_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(filter_label)
        controls_layout.addWidget(self.filter_combo)
        
        main_layout.addLayout(controls_layout)
        
        # Splitter for table and details
        splitter = QSplitter(Qt.Vertical)
        
        # Torrents table
        self.torrents_table = QTableWidget()
        self.torrents_table.setColumnCount(7)
        self.torrents_table.setHorizontalHeaderLabels([
            "Name", "Size", "Progress", "Status", "Speed", "ETA", "Ratio"
        ])
        
        # Table styling
        self.torrents_table.setStyleSheet("""
            QTableWidget {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            QTableWidget::item:selected {
                background: #383848;
            }
            QHeaderView::section {
                background: #232330;
                color: #e9d8a6;
                padding: 8px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """)
        
        # Table properties
        self.torrents_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.torrents_table.setAlternatingRowColors(True)
        self.torrents_table.horizontalHeader().setStretchLastSection(True)
        self.torrents_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.torrents_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        splitter.addWidget(self.torrents_table)
        
        # Details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_title = QLabel("Torrent Details")
        details_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        details_title.setStyleSheet("color: #e9d8a6; margin: 5px;")
        details_layout.addWidget(details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setFont(QFont("Consolas", 9))
        self.details_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        splitter.addWidget(details_widget)
        splitter.setStretchFactor(0, 3)  # Table gets more space
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Summary
        self.summary_label = QLabel("No torrents")
        self.summary_label.setStyleSheet("color: #888; font-size: 10px; margin: 5px;")
        main_layout.addWidget(self.summary_label)
        
        self.setLayout(main_layout)
        
    def setup_timer(self):
        """Setup timer for periodic updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_torrents)
        self.update_timer.start(3000)  # Update every 3 seconds
        
    def connect_qbittorrent(self):
        """Connect to qBittorrent client."""
        try:
            from utilities import QB_HOST, QB_PORT, QB_USER, QB_PASS
        except ImportError:
            # Use defaults if not imported
            QB_HOST = "127.0.0.1"
            QB_PORT = "8080"
            QB_USER = "admin"
            QB_PASS = "adminadmin"
            
        try:
            self.qb_client = qbittorrentapi.Client(
                host=f"http://{QB_HOST}:{QB_PORT}",
                username=QB_USER,
                password=QB_PASS
            )
            self.qb_client.auth_log_in()
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #a6e3a1; margin: 10px;")
            
        except Exception as e:
            self.status_label.setText(f"Connection failed: {str(e)[:30]}...")
            self.status_label.setStyleSheet("color: #f38ba8; margin: 10px;")
            self.qb_client = None
            
    def refresh_torrents(self):
        """Refresh the torrents list."""
        if not self.qb_client:
            self.connect_qbittorrent()
            return
            
        try:
            torrents = self.qb_client.torrents_info()
            self.torrents_data = torrents
            self.update_table()
            self.update_summary()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)[:30]}...")
            self.status_label.setStyleSheet("color: #f38ba8; margin: 10px;")
            
    def update_table(self):
        """Update the torrents table."""
        filter_text = self.filter_combo.currentText()
        
        # Filter torrents
        filtered_torrents = []
        for torrent in self.torrents_data:
            if filter_text == "All":
                filtered_torrents.append(torrent)
            elif filter_text.lower() in torrent.state.lower():
                filtered_torrents.append(torrent)
            elif filter_text == "Downloading" and "downloading" in torrent.state.lower():
                filtered_torrents.append(torrent)
            elif filter_text == "Completed" and torrent.progress == 1.0:
                filtered_torrents.append(torrent)
            elif filter_text == "Error" and "error" in torrent.state.lower():
                filtered_torrents.append(torrent)
                
        self.torrents_table.setRowCount(len(filtered_torrents))
        
        for row, torrent in enumerate(filtered_torrents):
            # Name
            name_item = QTableWidgetItem(torrent.name)
            self.torrents_table.setItem(row, 0, name_item)
            
            # Size
            size_item = QTableWidgetItem(format_file_size(torrent.size))
            self.torrents_table.setItem(row, 1, size_item)
            
            # Progress
            progress_text = f"{torrent.progress * 100:.1f}%"
            progress_item = QTableWidgetItem(progress_text)
            self.torrents_table.setItem(row, 2, progress_item)
            
            # Status
            status_item = QTableWidgetItem(torrent.state.title())
            # Color code status
            if "downloading" in torrent.state.lower():
                status_item.setBackground(Qt.darkGreen)
            elif "paused" in torrent.state.lower():
                status_item.setBackground(Qt.darkYellow)
            elif "error" in torrent.state.lower():
                status_item.setBackground(Qt.darkRed)
            elif torrent.progress == 1.0:
                status_item.setBackground(Qt.darkBlue)
                
            self.torrents_table.setItem(row, 3, status_item)
            
            # Speed
            speed_text = format_file_size(torrent.dlspeed) + "/s"
            speed_item = QTableWidgetItem(speed_text)
            self.torrents_table.setItem(row, 4, speed_item)
            
            # ETA
            eta_text = "∞" if torrent.eta == 8640000 else f"{torrent.eta // 3600}h {(torrent.eta % 3600) // 60}m"
            eta_item = QTableWidgetItem(eta_text)
            self.torrents_table.setItem(row, 5, eta_item)
            
            # Ratio
            ratio_item = QTableWidgetItem(f"{torrent.ratio:.2f}")
            self.torrents_table.setItem(row, 6, ratio_item)
            
            # Store torrent hash for actions
            name_item.setData(Qt.UserRole, torrent.hash)
            
    def filter_torrents(self):
        """Filter torrents based on selected filter."""
        self.update_table()
        
    def on_selection_changed(self):
        """Handle selection change in torrents table."""
        has_selection = len(self.torrents_table.selectedItems()) > 0
        
        self.pause_btn.setEnabled(has_selection)
        self.resume_btn.setEnabled(has_selection)
        self.remove_btn.setEnabled(has_selection)
        
        if has_selection:
            row = self.torrents_table.currentRow()
            if row >= 0:
                name_item = self.torrents_table.item(row, 0)
                if name_item:
                    torrent_hash = name_item.data(Qt.UserRole)
                    self.show_torrent_details(torrent_hash)
        else:
            self.details_text.clear()
            
    def show_torrent_details(self, torrent_hash):
        """Show details for the selected torrent."""
        for torrent in self.torrents_data:
            if torrent.hash == torrent_hash:
                details = f"<b>Name:</b> {torrent.name}<br>"
                details += f"<b>Hash:</b> {torrent.hash}<br>"
                details += f"<b>Size:</b> {format_file_size(torrent.size)}<br>"
                details += f"<b>Downloaded:</b> {format_file_size(torrent.downloaded)}<br>"
                details += f"<b>Uploaded:</b> {format_file_size(torrent.uploaded)}<br>"
                details += f"<b>Progress:</b> {torrent.progress * 100:.2f}%<br>"
                details += f"<b>State:</b> {torrent.state}<br>"
                details += f"<b>Priority:</b> {torrent.priority}<br>"
                details += f"<b>Category:</b> {torrent.category or 'None'}<br>"
                details += f"<b>Tags:</b> {torrent.tags or 'None'}<br>"
                details += f"<b>Save Path:</b> {torrent.save_path}<br>"
                
                self.details_text.setHtml(details)
                break
                
    def pause_selected(self):
        """Pause the selected torrent."""
        torrent_hash = self.get_selected_hash()
        if torrent_hash and self.qb_client:
            try:
                self.qb_client.torrents_pause(torrent_hash)
                self.refresh_torrents()
            except Exception as e:
                print(f"Error pausing torrent: {e}")
                
    def resume_selected(self):
        """Resume the selected torrent."""
        torrent_hash = self.get_selected_hash()
        if torrent_hash and self.qb_client:
            try:
                self.qb_client.torrents_resume(torrent_hash)
                self.refresh_torrents()
            except Exception as e:
                print(f"Error resuming torrent: {e}")
                
    def remove_selected(self):
        """Remove the selected torrent."""
        torrent_hash = self.get_selected_hash()
        if torrent_hash and self.qb_client:
            try:
                # Remove without deleting files
                self.qb_client.torrents_delete(delete_files=False, torrent_hashes=torrent_hash)
                self.refresh_torrents()
            except Exception as e:
                print(f"Error removing torrent: {e}")
                
    def get_selected_hash(self):
        """Get the hash of the selected torrent."""
        row = self.torrents_table.currentRow()
        if row >= 0:
            name_item = self.torrents_table.item(row, 0)
            if name_item:
                return name_item.data(Qt.UserRole)
        return None
        
    def update_summary(self):
        """Update the summary label."""
        if not self.torrents_data:
            self.summary_label.setText("No torrents")
            return
            
        total = len(self.torrents_data)
        downloading = sum(1 for t in self.torrents_data if "downloading" in t.state.lower())
        completed = sum(1 for t in self.torrents_data if t.progress == 1.0)
        paused = sum(1 for t in self.torrents_data if "paused" in t.state.lower())
        
        summary = f"Total: {total} | Downloading: {downloading} | Completed: {completed} | Paused: {paused}"
        self.summary_label.setText(summary)