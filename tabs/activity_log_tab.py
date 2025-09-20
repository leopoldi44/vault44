"""
Activity Log Tab for monitoring download activities and logs.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel,
    QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import os


class ActivityLogTab(QWidget):
    """Tab for displaying download activity logs."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Activity Log")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; margin: 10px;")
        main_layout.addWidget(title)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        clear_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 8px;
                padding: 6px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        clear_btn.clicked.connect(self.clear_log)
        
        # Auto-scroll checkbox would go here
        controls_layout.addWidget(clear_btn)
        controls_layout.addStretch()
        
        main_layout.addLayout(controls_layout)
        
        # Splitter for multiple log views
        splitter = QSplitter(Qt.Horizontal)
        
        # Main activity log
        self.activity_text = QTextEdit()
        self.activity_text.setFont(QFont("Consolas", 9))
        self.activity_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.activity_text.setReadOnly(True)
        
        # Download progress area
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        
        progress_title = QLabel("Download Progress")
        progress_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        progress_title.setStyleSheet("color: #e9d8a6; margin: 5px;")
        progress_layout.addWidget(progress_title)
        
        self.progress_text = QTextEdit()
        self.progress_text.setFont(QFont("Consolas", 8))
        self.progress_text.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #a6e3a1;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(200)
        progress_layout.addWidget(self.progress_text)
        
        splitter.addWidget(self.activity_text)
        splitter.addWidget(progress_widget)
        splitter.setStretchFactor(0, 2)  # Main log gets more space
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Add some initial content
        self.add_log_entry("Activity log initialized", "INFO")
        
    def setup_timer(self):
        """Setup timer for periodic log updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_logs)
        self.update_timer.start(2000)  # Update every 2 seconds
        
    def add_log_entry(self, message, level="INFO"):
        """Add an entry to the activity log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color based on level
        colors = {
            "INFO": "#e9d8a6",
            "SUCCESS": "#a6e3a1", 
            "WARNING": "#f9e2af",
            "ERROR": "#f38ba8"
        }
        color = colors.get(level, "#e9d8a6")
        
        formatted_message = f"<span style='color: #666;'>[{timestamp}]</span> <span style='color: {color};'>[{level}]</span> {message}"
        self.activity_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.activity_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def add_progress_update(self, message):
        """Add a progress update entry."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"<span style='color: #666;'>[{timestamp}]</span> {message}"
        self.progress_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.progress_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_log(self):
        """Clear the activity log."""
        self.activity_text.clear()
        self.add_log_entry("Log cleared", "INFO")
        
    def update_logs(self):
        """Update logs from external sources if needed."""
        # This could read from log files or other sources
        # For now, it's a placeholder for future implementation
        pass