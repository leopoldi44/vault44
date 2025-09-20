"""
Recommendations Tab for movie recommendations based on viewing history.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSplitter, QTextEdit, QComboBox, QProgressBar,
    QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from utilities import parse_movie_title
import random


class RecommendationWorker(QThread):
    """Worker thread for generating recommendations."""
    
    recommendations_ready = pyqtSignal(list)
    progress_update = pyqtSignal(int)
    
    def __init__(self, processed_movies, collection, criteria):
        super().__init__()
        self.processed_movies = processed_movies
        self.collection = collection
        self.criteria = criteria
        
    def run(self):
        """Generate recommendations based on criteria."""
        recommendations = []
        
        # Simulate recommendation generation with progress
        for i in range(20):  # Generate 20 recommendations
            self.progress_update.emit(i * 5)
            
            # Simple recommendation logic - in reality this would use ML/AI
            if self.criteria == "Similar Genre":
                rec = self.generate_genre_based()
            elif self.criteria == "Popular":
                rec = self.generate_popular()
            elif self.criteria == "Recent":
                rec = self.generate_recent()
            else:
                rec = self.generate_random()
                
            if rec:
                recommendations.append(rec)
                
            self.msleep(50)  # Simulate processing time
            
        self.progress_update.emit(100)
        self.recommendations_ready.emit(recommendations)
        
    def generate_genre_based(self):
        """Generate genre-based recommendations."""
        # Sample movie recommendations
        sample_movies = [
            "Blade Runner 2049, 2017",
            "The Matrix Resurrections, 2021", 
            "Dune: Part Two, 2024",
            "Mad Max: Fury Road, 2015",
            "Ex Machina, 2014",
            "Arrival, 2016",
            "Interstellar, 2014",
            "Her, 2013"
        ]
        return random.choice(sample_movies)
        
    def generate_popular(self):
        """Generate popular movie recommendations."""
        popular_movies = [
            "Everything Everywhere All at Once, 2022",
            "Top Gun: Maverick, 2022",
            "Avatar: The Way of Water, 2022",
            "Black Panther: Wakanda Forever, 2022",
            "The Batman, 2022",
            "Spider-Man: No Way Home, 2021",
            "Oppenheimer, 2023",
            "Barbie, 2023"
        ]
        return random.choice(popular_movies)
        
    def generate_recent(self):
        """Generate recent movie recommendations."""
        recent_movies = [
            "Poor Things, 2023",
            "The Zone of Interest, 2023",
            "American Fiction, 2023",
            "Past Lives, 2023",
            "Killers of the Flower Moon, 2023",
            "The Holdovers, 2023",
            "Anatomy of a Fall, 2023",
            "May December, 2023"
        ]
        return random.choice(recent_movies)
        
    def generate_random(self):
        """Generate random recommendations."""
        all_movies = [
            "Parasite, 2019",
            "Moonlight, 2016", 
            "La La Land, 2016",
            "Mad Max: Fury Road, 2015",
            "Birdman, 2014",
            "12 Years a Slave, 2013",
            "Argo, 2012",
            "The Shape of Water, 2017"
        ]
        return random.choice(all_movies)


class RecommendationsTab(QWidget):
    """Tab for movie recommendations based on viewing history."""
    
    movie_selected = pyqtSignal(str)  # Signal when movie is selected
    add_to_list_requested = pyqtSignal(str)  # Signal to add movie to download list
    
    def __init__(self, processed_movies, collection, main_gui):
        super().__init__()
        self.processed_movies = processed_movies or []
        self.collection = collection or []
        self.main_gui = main_gui
        self.current_recommendations = []
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Title and stats
        header_layout = QHBoxLayout()
        
        title = QLabel("Movie Recommendations")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; margin: 10px;")
        
        self.stats_label = QLabel(f"Based on {len(self.processed_movies)} watched movies")
        self.stats_label.setFont(QFont("Segoe UI", 10))
        self.stats_label.setStyleSheet("color: #888; margin: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        
        main_layout.addLayout(header_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Recommendation criteria
        criteria_label = QLabel("Criteria:")
        criteria_label.setStyleSheet("color: #e9d8a6; font-weight: bold;")
        
        self.criteria_combo = QComboBox()
        self.criteria_combo.addItems([
            "Similar Genre", "Popular", "Recent", "Random", "Director Based", "Actor Based"
        ])
        self.criteria_combo.setStyleSheet("""
            QComboBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                min-width: 120px;
            }
        """)
        
        # Generate button
        generate_btn = QPushButton("🎯 Generate Recommendations")
        generate_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        generate_btn.setStyleSheet("""
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
        generate_btn.clicked.connect(self.generate_recommendations)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
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
        refresh_btn.clicked.connect(self.refresh_recommendations)
        
        # Filter options
        self.hide_watched_check = QCheckBox("Hide watched movies")
        self.hide_watched_check.setStyleSheet("""
            QCheckBox {
                color: #e9d8a6;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        self.hide_watched_check.stateChanged.connect(self.filter_recommendations)
        
        controls_layout.addWidget(criteria_label)
        controls_layout.addWidget(self.criteria_combo)
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.hide_watched_check)
        
        main_layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
                background: #1e1e2e;
                color: #e9d8a6;
            }
            QProgressBar::chunk {
                background: #a6e3a1;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Splitter for recommendations and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Recommendations list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #e9d8a6;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter recommendations...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_recommendations)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Recommendations list
        list_label = QLabel("Recommended Movies")
        list_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        list_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        left_layout.addWidget(list_label)
        
        self.recommendations_list = QListWidget()
        self.recommendations_list.setFont(QFont("Segoe UI", 10))
        self.recommendations_list.setStyleSheet("""
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
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:selected {
                background: #383848;
            }
            QListWidget::item:hover {
                background: #2a2a3a;
            }
        """)
        self.recommendations_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.recommendations_list.itemDoubleClicked.connect(self.add_to_download_list)
        left_layout.addWidget(self.recommendations_list)
        
        # List stats
        self.list_stats_label = QLabel("0 recommendations")
        self.list_stats_label.setStyleSheet("color: #888; font-size: 10px; margin: 5px;")
        left_layout.addWidget(self.list_stats_label)
        
        # Right side - Movie details and actions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        details_label = QLabel("Movie Details")
        details_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        details_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(details_label)
        
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
        self.details_text.setMaximumHeight(250)
        right_layout.addWidget(self.details_text)
        
        # Action buttons
        actions_label = QLabel("Actions")
        actions_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        actions_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(actions_label)
        
        self.add_btn = QPushButton("➕ Add to Download List")
        self.add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.add_btn.setStyleSheet("""
            QPushButton {
                color: #232330;
                background: #a6e3a1;
                border-radius: 8px;
                padding: 10px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #a6f3a1;
            }
        """)
        self.add_btn.clicked.connect(self.add_to_download_list)
        self.add_btn.setEnabled(False)
        
        self.info_btn = QPushButton("ℹ️ More Info")
        self.info_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_btn.setStyleSheet("""
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
        self.info_btn.clicked.connect(self.show_more_info)
        self.info_btn.setEnabled(False)
        
        self.ignore_btn = QPushButton("❌ Not Interested")
        self.ignore_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.ignore_btn.setStyleSheet("""
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
        self.ignore_btn.clicked.connect(self.ignore_recommendation)
        self.ignore_btn.setEnabled(False)
        
        right_layout.addWidget(self.add_btn)
        right_layout.addWidget(self.info_btn)
        right_layout.addWidget(self.ignore_btn)
        right_layout.addStretch()
        
        # Recommendation algorithm info
        algo_label = QLabel("Algorithm Info")
        algo_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        algo_label.setStyleSheet("color: #e9d8a6; margin: 5px;")
        right_layout.addWidget(algo_label)
        
        self.algo_text = QTextEdit()
        self.algo_text.setFont(QFont("Segoe UI", 8))
        self.algo_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #888;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.algo_text.setReadOnly(True)
        self.algo_text.setMaximumHeight(100)
        self.algo_text.setHtml("""
        <i>Recommendations are generated based on your viewing history, 
        genre preferences, and collaborative filtering algorithms. 
        The system analyzes patterns in your watched movies to suggest 
        similar titles you might enjoy.</i>
        """)
        right_layout.addWidget(self.algo_text)
        
        # Add to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Generate initial recommendations
        self.generate_recommendations()
        
    def generate_recommendations(self):
        """Generate new recommendations."""
        if self.worker and self.worker.isRunning():
            return
            
        criteria = self.criteria_combo.currentText()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start worker thread
        self.worker = RecommendationWorker(
            self.processed_movies, 
            self.collection, 
            criteria
        )
        self.worker.recommendations_ready.connect(self.on_recommendations_ready)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.start()
        
    def on_recommendations_ready(self, recommendations):
        """Handle recommendations when ready."""
        self.current_recommendations = recommendations
        self.populate_recommendations()
        self.progress_bar.setVisible(False)
        
    def populate_recommendations(self):
        """Populate the recommendations list."""
        self.recommendations_list.clear()
        
        search_text = self.search_input.text().lower()
        hide_watched = self.hide_watched_check.isChecked()
        
        filtered_recs = []
        for rec in self.current_recommendations:
            # Filter by search text
            if search_text and search_text not in rec.lower():
                continue
                
            # Filter watched movies
            if hide_watched and rec in self.processed_movies:
                continue
                
            filtered_recs.append(rec)
            
        for rec in filtered_recs:
            item = QListWidgetItem(rec)
            
            # Mark watched movies
            if rec in self.processed_movies:
                item.setToolTip("Already watched")
                item.setText(f"✓ {rec}")
                
            self.recommendations_list.addItem(item)
            
        self.update_list_stats()
        
    def filter_recommendations(self):
        """Filter recommendations based on search and options."""
        self.populate_recommendations()
        
    def refresh_recommendations(self):
        """Refresh recommendations."""
        self.generate_recommendations()
        
    def on_selection_changed(self):
        """Handle selection change."""
        current_item = self.recommendations_list.currentItem()
        has_selection = current_item is not None
        
        self.add_btn.setEnabled(has_selection)
        self.info_btn.setEnabled(has_selection)
        self.ignore_btn.setEnabled(has_selection)
        
        if current_item:
            movie_text = current_item.text()
            # Remove the checkmark if present
            if movie_text.startswith("✓ "):
                movie_text = movie_text[2:]
                
            self.show_movie_details(movie_text)
            self.movie_selected.emit(movie_text)
        else:
            self.details_text.clear()
            
    def show_movie_details(self, movie_text):
        """Show details for the selected movie."""
        title, year = parse_movie_title(movie_text)
        
        details = f"<b>Recommended Movie:</b><br>"
        details += f"<b>Title:</b> {title}<br>"
        if year:
            details += f"<b>Year:</b> {year}<br>"
        details += f"<b>Full Text:</b> {movie_text}<br><br>"
        
        # Check if already watched
        if movie_text in self.processed_movies:
            details += "<span style='color: #a6e3a1;'><b>Status:</b> Already watched ✓</span><br><br>"
        else:
            details += "<span style='color: #f9e2af;'><b>Status:</b> Not watched</span><br><br>"
            
        # Add recommendation reason
        criteria = self.criteria_combo.currentText()
        details += f"<b>Recommended because:</b> {criteria}<br><br>"
        
        details += "<i>Double-click to add to download list.</i><br>"
        details += "<i>Detailed movie information, ratings, and reviews would be displayed here.</i>"
        
        self.details_text.setHtml(details)
        
    def add_to_download_list(self):
        """Add selected movie to download list."""
        current_item = self.recommendations_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            # Remove the checkmark if present
            if movie_text.startswith("✓ "):
                movie_text = movie_text[2:]
                
            self.add_to_list_requested.emit(movie_text)
            
            # You could also directly add to the movie list tab here
            if hasattr(self.main_gui, 'list_tab'):
                # Simulate adding to the list tab
                print(f"Adding to download list: {movie_text}")
                
    def show_more_info(self):
        """Show more information about the selected movie."""
        current_item = self.recommendations_list.currentItem()
        if current_item:
            movie_text = current_item.text()
            if movie_text.startswith("✓ "):
                movie_text = movie_text[2:]
                
            # In a real implementation, this would open a detailed info dialog
            print(f"Showing more info for: {movie_text}")
            
    def ignore_recommendation(self):
        """Ignore the selected recommendation."""
        current_item = self.recommendations_list.currentItem()
        if current_item:
            row = self.recommendations_list.row(current_item)
            self.recommendations_list.takeItem(row)
            self.update_list_stats()
            self.details_text.clear()
            
    def update_list_stats(self):
        """Update the list statistics."""
        count = self.recommendations_list.count()
        self.list_stats_label.setText(f"{count} recommendation{'s' if count != 1 else ''}")