"""
Movie List Tab for managing movie download lists.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QSplitter,
    QTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utilities import read_file_lines, write_file_lines, parse_movie_title


class MovieListTab(QWidget):
    """Tab for managing movie download lists."""
    
    movie_added = pyqtSignal(str)  # Signal when movie is added
    movie_removed = pyqtSignal(str)  # Signal when movie is removed
    
    def __init__(self, movie_list_path):
        super().__init__()
        self.movie_list_path = movie_list_path
        self.init_ui()
        self.load_movie_list()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Movie Download List")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; margin: 10px;")
        main_layout.addWidget(title)
        
        # Top controls
        top_controls = QHBoxLayout()
        
        # Add movie section
        self.movie_input = QLineEdit()
        self.movie_input.setPlaceholderText("Enter movie title, year (optional)")
        self.movie_input.setFont(QFont("Segoe UI", 10))
        self.movie_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.movie_input.returnPressed.connect(self.add_movie)
        
        add_btn = QPushButton("Add Movie")
        add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_movie)
        
        top_controls.addWidget(QLabel("Add Movie:"))
        top_controls.addWidget(self.movie_input)
        top_controls.addWidget(add_btn)
        top_controls.addStretch()
        
        main_layout.addLayout(top_controls)
        
        # Splitter for movie list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Movie list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # List controls
        list_controls = QHBoxLayout()
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        remove_btn.setStyleSheet("""
            QPushButton {
                color: #fffbe6;
                background: #f38ba8;
                border-radius: 6px;
                padding: 6px 12px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #ff6b9d;
            }
        """)
        remove_btn.clicked.connect(self.remove_selected)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        clear_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 6px;
                padding: 6px 12px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        clear_btn.clicked.connect(self.clear_all)
        
        import_btn = QPushButton("Import List")
        import_btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        import_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 6px;
                padding: 6px 12px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        import_btn.clicked.connect(self.import_list)
        
        list_controls.addWidget(remove_btn)
        list_controls.addWidget(clear_btn)
        list_controls.addWidget(import_btn)
        list_controls.addStretch()
        
        left_layout.addLayout(list_controls)
        
        # Movie list widget
        self.movie_list = QListWidget()
        self.movie_list.setFont(QFont("Segoe UI", 10))
        self.movie_list.setStyleSheet("""
            QListWidget {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background: #383848;
            }
            QListWidget::item:hover {
                background: #2a2a3a;
            }
        """)
        self.movie_list.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.movie_list)
        
        # List stats
        self.stats_label = QLabel("0 movies in list")
        self.stats_label.setStyleSheet("color: #888; font-size: 10px; margin: 5px;")
        left_layout.addWidget(self.stats_label)
        
        # Right side - Movie details/preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        details_title = QLabel("Movie Details")
        details_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        details_title.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setFont(QFont("Segoe UI", 10))
        self.details_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        right_layout.addWidget(self.details_text)
        
        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        actions_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(actions_label)
        
        # Priority checkbox
        self.priority_check = QCheckBox("High Priority")
        self.priority_check.setStyleSheet("""
            QCheckBox {
                color: #e9d8a6;
                font-size: 10px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        right_layout.addWidget(self.priority_check)
        
        right_layout.addStretch()
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)  # List gets more space
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def load_movie_list(self):
        """Load movies from the file."""
        movies = read_file_lines(self.movie_list_path)
        self.movie_list.clear()
        
        for movie in movies:
            if movie.strip():
                item = QListWidgetItem(movie)
                self.movie_list.addItem(item)
                
        self.update_stats()
        
    def save_movie_list(self):
        """Save movies to the file."""
        movies = []
        for i in range(self.movie_list.count()):
            item = self.movie_list.item(i)
            movies.append(item.text())
            
        write_file_lines(self.movie_list_path, movies)
        
    def add_movie(self):
        """Add a movie to the list."""
        movie_text = self.movie_input.text().strip()
        if not movie_text:
            return
            
        # Check for duplicates
        for i in range(self.movie_list.count()):
            if self.movie_list.item(i).text().lower() == movie_text.lower():
                QMessageBox.warning(self, "Duplicate", "This movie is already in the list.")
                return
                
        # Add the movie
        item = QListWidgetItem(movie_text)
        self.movie_list.addItem(item)
        self.movie_input.clear()
        self.save_movie_list()
        self.update_stats()
        
        # Emit signal
        self.movie_added.emit(movie_text)
        
    def remove_selected(self):
        """Remove the selected movie from the list."""
        current_item = self.movie_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            row = self.movie_list.row(current_item)
            self.movie_list.takeItem(row)
            self.save_movie_list()
            self.update_stats()
            
            # Emit signal
            self.movie_removed.emit(movie_text)
            
    def clear_all(self):
        """Clear all movies from the list."""
        reply = QMessageBox.question(self, "Clear All", 
                                   "Are you sure you want to clear all movies?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.movie_list.clear()
            self.save_movie_list()
            self.update_stats()
            self.details_text.clear()
            
    def import_list(self):
        """Import movies from a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Movie List", "", 
            "Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            imported_movies = read_file_lines(file_path)
            added_count = 0
            
            for movie in imported_movies:
                movie = movie.strip()
                if movie:
                    # Check for duplicates
                    duplicate = False
                    for i in range(self.movie_list.count()):
                        if self.movie_list.item(i).text().lower() == movie.lower():
                            duplicate = True
                            break
                    
                    if not duplicate:
                        item = QListWidgetItem(movie)
                        self.movie_list.addItem(item)
                        added_count += 1
                        
            self.save_movie_list()
            self.update_stats()
            
            QMessageBox.information(self, "Import Complete", 
                                  f"Added {added_count} new movies to the list.")
            
    def on_selection_changed(self):
        """Handle selection change in the movie list."""
        current_item = self.movie_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            title, year = parse_movie_title(movie_text)
            
            details = f"<b>Selected Movie:</b><br>"
            details += f"<b>Title:</b> {title}<br>"
            if year:
                details += f"<b>Year:</b> {year}<br>"
            details += f"<b>Full Text:</b> {movie_text}<br><br>"
            details += "<i>Movie details and metadata would be displayed here.</i>"
            
            self.details_text.setHtml(details)
        else:
            self.details_text.clear()
            
    def update_stats(self):
        """Update the statistics label."""
        count = self.movie_list.count()
        self.stats_label.setText(f"{count} movie{'s' if count != 1 else ''} in list")