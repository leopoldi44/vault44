"""
Next Up Tab for managing movies to watch next.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSplitter, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class NextUpTab(QWidget):
    """Tab for managing next up movies to watch."""
    
    play_requested = pyqtSignal(str)  # Signal when play is requested
    
    def __init__(self, planned_movies, play_callback=None):
        super().__init__()
        self.planned_movies = planned_movies
        self.play_callback = play_callback
        self.init_ui()
        self.load_planned_movies()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Next Up - Movies to Watch")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; margin: 10px;")
        main_layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh List")
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
        refresh_btn.clicked.connect(self.refresh_list)
        
        mark_watched_btn = QPushButton("Mark as Watched")
        mark_watched_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        mark_watched_btn.setStyleSheet("""
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
        mark_watched_btn.clicked.connect(self.mark_as_watched)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(mark_watched_btn)
        controls_layout.addStretch()
        
        main_layout.addLayout(controls_layout)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Movies list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        list_label = QLabel("Planned Movies")
        list_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        list_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        left_layout.addWidget(list_label)
        
        self.movies_list = QListWidget()
        self.movies_list.setFont(QFont("Segoe UI", 11))
        self.movies_list.setStyleSheet("""
            QListWidget {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
                border-radius: 3px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: #383848;
            }
            QListWidget::item:hover {
                background: #2a2a3a;
            }
        """)
        self.movies_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.movies_list.itemDoubleClicked.connect(self.on_double_click)
        left_layout.addWidget(self.movies_list)
        
        # Stats
        self.stats_label = QLabel("0 movies planned")
        self.stats_label.setStyleSheet("color: #888; font-size: 10px; margin: 5px;")
        left_layout.addWidget(self.stats_label)
        
        # Right side - Movie info and actions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        info_label = QLabel("Movie Information")
        info_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        info_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setFont(QFont("Segoe UI", 10))
        self.info_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        right_layout.addWidget(self.info_text)
        
        # Action buttons
        actions_label = QLabel("Actions")
        actions_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        actions_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(actions_label)
        
        self.play_btn = QPushButton("▶ Play Movie")
        self.play_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.play_btn.setStyleSheet("""
            QPushButton {
                color: #232330;
                background: #f9e2af;
                border-radius: 8px;
                padding: 10px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #f9f2cf;
            }
        """)
        self.play_btn.clicked.connect(self.play_selected)
        self.play_btn.setEnabled(False)
        
        self.search_btn = QPushButton("🔍 Search Online")
        self.search_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.search_btn.setStyleSheet("""
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
        self.search_btn.clicked.connect(self.search_online)
        self.search_btn.setEnabled(False)
        
        right_layout.addWidget(self.play_btn)
        right_layout.addWidget(self.search_btn)
        right_layout.addStretch()
        
        # Add to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def load_planned_movies(self):
        """Load planned movies into the list."""
        self.movies_list.clear()
        
        for movie in self.planned_movies:
            if movie.strip():
                item = QListWidgetItem(movie)
                # Add some visual indicators
                if "2024" in movie or "2025" in movie:
                    item.setToolTip("Recent movie")
                self.movies_list.addItem(item)
                
        self.update_stats()
        
    def refresh_list(self):
        """Refresh the planned movies list."""
        # In a real implementation, this would reload from the source
        self.load_planned_movies()
        
    def mark_as_watched(self):
        """Mark the selected movie as watched."""
        current_item = self.movies_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            # In a real implementation, this would move the movie to watched list
            # For now, just remove it from this list
            row = self.movies_list.row(current_item)
            self.movies_list.takeItem(row)
            self.update_stats()
            self.info_text.clear()
            
            # Could emit a signal here to notify other components
            print(f"Marked as watched: {movie_text}")
            
    def on_selection_changed(self):
        """Handle selection change."""
        current_item = self.movies_list.currentItem()
        has_selection = current_item is not None
        
        self.play_btn.setEnabled(has_selection)
        self.search_btn.setEnabled(has_selection)
        
        if current_item:
            movie_text = current_item.text()
            
            # Parse movie info
            info = f"<b>Selected Movie:</b><br>{movie_text}<br><br>"
            
            # Try to extract year
            if "," in movie_text:
                parts = movie_text.split(",")
                if len(parts) >= 2:
                    title = ",".join(parts[:-1]).strip()
                    year = parts[-1].strip()
                    info += f"<b>Title:</b> {title}<br>"
                    info += f"<b>Year:</b> {year}<br><br>"
            
            info += "<i>Double-click to play or use the Play button below.</i><br>"
            info += "<i>Movie metadata and ratings would be displayed here.</i>"
            
            self.info_text.setHtml(info)
        else:
            self.info_text.clear()
            
    def on_double_click(self, item):
        """Handle double-click on movie item."""
        self.play_selected()
        
    def play_selected(self):
        """Play the selected movie."""
        current_item = self.movies_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            
            if self.play_callback:
                self.play_callback(movie_text)
            
            self.play_requested.emit(movie_text)
            
    def search_online(self):
        """Search for the selected movie online."""
        current_item = self.movies_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            
            # Extract title for search
            title = movie_text
            if "," in movie_text:
                title = movie_text.split(",")[0].strip()
            
            # In a real implementation, this would open a web browser
            # or trigger a search in the application
            print(f"Searching online for: {title}")
            
    def update_stats(self):
        """Update the statistics label."""
        count = self.movies_list.count()
        self.stats_label.setText(f"{count} movie{'s' if count != 1 else ''} planned")