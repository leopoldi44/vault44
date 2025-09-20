"""
Settings Tab for application configuration.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QSpinBox, QFileDialog, 
    QCheckBox, QComboBox, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utilities import load_settings, save_settings
import os


class SettingsTab(QWidget):
    """Tab for application settings and configuration."""
    
    settings_changed = pyqtSignal(dict)  # Signal when settings change
    
    def __init__(self, main_gui):
        super().__init__()
        self.main_gui = main_gui
        self.gui = main_gui  # For backward compatibility
        self.settings = load_settings()
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Create scroll area for all settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Title
        title = QLabel("Application Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #e9d8a6; margin: 10px;")
        main_layout.addWidget(title)
        
        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        download_group.setStyleSheet("""
            QGroupBox {
                color: #e9d8a6;
                border: 2px solid #555;
                border-radius: 8px;
                margin: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        download_layout = QFormLayout()
        
        # Save Path
        self.save_path_input = QLineEdit()
        self.save_path_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        browse_btn.clicked.connect(self.browse_save_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.save_path_input)
        path_layout.addWidget(browse_btn)
        
        download_layout.addRow("Save Path:", path_layout)
        
        # Max Active Torrents
        self.max_torrents_spin = QSpinBox()
        self.max_torrents_spin.setRange(1, 20)
        self.max_torrents_spin.setStyleSheet("""
            QSpinBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        download_layout.addRow("Max Active Torrents:", self.max_torrents_spin)
        
        # Auto-start downloads
        self.auto_start_check = QCheckBox("Auto-start downloads")
        self.auto_start_check.setStyleSheet("""
            QCheckBox {
                color: #e9d8a6;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        download_layout.addRow("", self.auto_start_check)
        
        download_group.setLayout(download_layout)
        main_layout.addWidget(download_group)
        
        # qBittorrent Settings Group
        qb_group = QGroupBox("qBittorrent Connection")
        qb_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        qb_group.setStyleSheet("""
            QGroupBox {
                color: #e9d8a6;
                border: 2px solid #555;
                border-radius: 8px;
                margin: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        qb_layout = QFormLayout()
        
        # Host
        self.qb_host_input = QLineEdit()
        self.qb_host_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        qb_layout.addRow("Host:", self.qb_host_input)
        
        # Port
        self.qb_port_spin = QSpinBox()
        self.qb_port_spin.setRange(1, 65535)
        self.qb_port_spin.setValue(8080)
        self.qb_port_spin.setStyleSheet("""
            QSpinBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        qb_layout.addRow("Port:", self.qb_port_spin)
        
        # Username
        self.qb_user_input = QLineEdit()
        self.qb_user_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        qb_layout.addRow("Username:", self.qb_user_input)
        
        # Password
        self.qb_pass_input = QLineEdit()
        self.qb_pass_input.setEchoMode(QLineEdit.Password)
        self.qb_pass_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        qb_layout.addRow("Password:", self.qb_pass_input)
        
        # Test connection button
        test_btn = QPushButton("Test Connection")
        test_btn.setStyleSheet("""
            QPushButton {
                color: #232330;
                background: #f9e2af;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #f9f2cf;
            }
        """)
        test_btn.clicked.connect(self.test_qb_connection)
        qb_layout.addRow("", test_btn)
        
        qb_group.setLayout(qb_layout)
        main_layout.addWidget(qb_group)
        
        # Interface Settings Group
        ui_group = QGroupBox("Interface Settings")
        ui_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        ui_group.setStyleSheet("""
            QGroupBox {
                color: #e9d8a6;
                border: 2px solid #555;
                border-radius: 8px;
                margin: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        ui_layout = QFormLayout()
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        ui_layout.addRow("Theme:", self.theme_combo)
        
        # Auto-refresh interval
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 60)
        self.refresh_spin.setValue(3)
        self.refresh_spin.setSuffix(" seconds")
        self.refresh_spin.setStyleSheet("""
            QSpinBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        ui_layout.addRow("Refresh Interval:", self.refresh_spin)
        
        # Show notifications
        self.notifications_check = QCheckBox("Show notifications")
        self.notifications_check.setStyleSheet("""
            QCheckBox {
                color: #e9d8a6;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        ui_layout.addRow("", self.notifications_check)
        
        # Minimize to tray
        self.tray_check = QCheckBox("Minimize to system tray")
        self.tray_check.setStyleSheet("""
            QCheckBox {
                color: #e9d8a6;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        ui_layout.addRow("", self.tray_check)
        
        ui_group.setLayout(ui_layout)
        main_layout.addWidget(ui_group)
        
        # Advanced Settings Group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        advanced_group.setStyleSheet("""
            QGroupBox {
                color: #e9d8a6;
                border: 2px solid #555;
                border-radius: 8px;
                margin: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        advanced_layout = QFormLayout()
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.setStyleSheet("""
            QComboBox {
                background: #1e1e2e;
                color: #e9d8a6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        advanced_layout.addRow("Log Level:", self.log_level_combo)
        
        # Debug mode
        self.debug_check = QCheckBox("Debug mode")
        self.debug_check.setStyleSheet("""
            QCheckBox {
                color: #e9d8a6;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        advanced_layout.addRow("", self.debug_check)
        
        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                color: #232330;
                background: #a6e3a1;
                border-radius: 8px;
                padding: 10px 20px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #a6f3a1;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        reset_btn.setStyleSheet("""
            QPushButton {
                color: #e9d8a6;
                background: #232330;
                border-radius: 8px;
                padding: 10px 20px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background: #282838;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        scroll.setWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)
        
    def load_current_settings(self):
        """Load current settings into the form."""
        # Download settings
        self.save_path_input.setText(self.settings.get("save_path", "downloads"))
        self.max_torrents_spin.setValue(self.settings.get("max_active_torrents", 3))
        self.auto_start_check.setChecked(self.settings.get("auto_start", True))
        
        # qBittorrent settings
        self.qb_host_input.setText(self.settings.get("qb_host", "127.0.0.1"))
        self.qb_port_spin.setValue(self.settings.get("qb_port", 8080))
        self.qb_user_input.setText(self.settings.get("qb_user", "admin"))
        self.qb_pass_input.setText(self.settings.get("qb_pass", "adminadmin"))
        
        # Interface settings
        self.theme_combo.setCurrentText(self.settings.get("theme", "Dark"))
        self.refresh_spin.setValue(self.settings.get("refresh_interval", 3))
        self.notifications_check.setChecked(self.settings.get("show_notifications", True))
        self.tray_check.setChecked(self.settings.get("minimize_to_tray", False))
        
        # Advanced settings
        self.log_level_combo.setCurrentText(self.settings.get("log_level", "INFO"))
        self.debug_check.setChecked(self.settings.get("debug_mode", False))
        
    def browse_save_path(self):
        """Browse for save path directory."""
        current_path = self.save_path_input.text()
        if not current_path or not os.path.exists(current_path):
            current_path = os.path.expanduser("~")
            
        directory = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", current_path
        )
        
        if directory:
            self.save_path_input.setText(directory)
            
    def test_qb_connection(self):
        """Test connection to qBittorrent."""
        try:
            import qbittorrentapi
            
            host = self.qb_host_input.text()
            port = self.qb_port_spin.value()
            user = self.qb_user_input.text()
            password = self.qb_pass_input.text()
            
            client = qbittorrentapi.Client(
                host=f"http://{host}:{port}",
                username=user,
                password=password
            )
            client.auth_log_in()
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Connection Test", 
                                  "Successfully connected to qBittorrent!")
                                  
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Connection Test", 
                              f"Failed to connect to qBittorrent:\n{str(e)}")
            
    def save_settings(self):
        """Save all settings."""
        new_settings = {
            # Download settings
            "save_path": self.save_path_input.text(),
            "max_active_torrents": self.max_torrents_spin.value(),
            "auto_start": self.auto_start_check.isChecked(),
            
            # qBittorrent settings
            "qb_host": self.qb_host_input.text(),
            "qb_port": self.qb_port_spin.value(),
            "qb_user": self.qb_user_input.text(),
            "qb_pass": self.qb_pass_input.text(),
            
            # Interface settings
            "theme": self.theme_combo.currentText(),
            "refresh_interval": self.refresh_spin.value(),
            "show_notifications": self.notifications_check.isChecked(),
            "minimize_to_tray": self.tray_check.isChecked(),
            
            # Advanced settings
            "log_level": self.log_level_combo.currentText(),
            "debug_mode": self.debug_check.isChecked()
        }
        
        if save_settings(new_settings):
            self.settings = new_settings
            
            # Update main GUI settings
            if hasattr(self.main_gui, 'save_path'):
                self.main_gui.save_path = new_settings["save_path"]
                if hasattr(self.main_gui, 'folder_label'):
                    self.main_gui.folder_label.setText(f"Save Folder: {new_settings['save_path']}")
            
            if hasattr(self.main_gui, 'max_active_torrents'):
                self.main_gui.max_active_torrents = new_settings["max_active_torrents"]
            
            # Emit signal
            self.settings_changed.emit(new_settings)
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings", "Failed to save settings!")
            
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Set default values
            self.save_path_input.setText("downloads")
            self.max_torrents_spin.setValue(3)
            self.auto_start_check.setChecked(True)
            
            self.qb_host_input.setText("127.0.0.1")
            self.qb_port_spin.setValue(8080)
            self.qb_user_input.setText("admin")
            self.qb_pass_input.setText("adminadmin")
            
            self.theme_combo.setCurrentText("Dark")
            self.refresh_spin.setValue(3)
            self.notifications_check.setChecked(True)
            self.tray_check.setChecked(False)
            
            self.log_level_combo.setCurrentText("INFO")
            self.debug_check.setChecked(False)