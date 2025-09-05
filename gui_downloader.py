import sys
import os
import requests
import subprocess
import threading
import csv
import random
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel,
    QPushButton, QFileDialog, QHBoxLayout, QLineEdit, QListWidget, QMessageBox,
    QSpacerItem, QSizePolicy, QFrame, QGraphicsDropShadowEffect, QComboBox,
    QCheckBox, QListWidgetItem, QSpinBox
)
from PyQt5.QtGui import (
    QFont, QPalette, QLinearGradient, QBrush, QColor, QTextCursor, QPixmap
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QObject
)

PROCESSED_MOVIES_FILE = "processed_movies.txt"
COLLECTION_FILE = "leo_movie_collection.csv"
DOWNLOAD_LIST_FILE = "movie_list.txt"
SETTINGS_FILE = "settings.json"
TMDB_API_KEY = "49ed1beab7e0a0ca5584b21be8d533ce"
QB_HOST = "localhost"
QB_PORT = 8080
QB_USER = "admin"
QB_PASS = "adminadmin"

LANGUAGES = {
    "Any": "",
    "Italy": "it",
    "United States": "en",
    "United Kingdom": "en",
    "France": "fr",
    "Germany": "de",
    "Japan": "ja",
    "Spain": "es",
    "South Korea": "ko"
}

CURATED_KEYWORDS = {
    "Cult": "12377",
    "Noir": "818",
    "Arthouse": "616",
    "Classic": "176223",
    "Festival": "10913"
}

def print_exception(e):
    print(f"Exception: {e}", flush=True)
    import traceback
    traceback.print_exc()

def read_file_lines(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print_exception(e)
    return []

def write_file_lines(filepath, lines):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    except Exception as e:
        print_exception(e)

def tmdb_get_genres():
    try:
        url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return {str(g['id']): g['name'] for g in data.get('genres', [])}
    except Exception as e:
        print_exception(e)
        return {}

def tmdb_fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=credits"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data
    except Exception as e:
        print_exception(e)
        return {}

def tmdb_fetch_movie_poster_url(movie_id):
    details = tmdb_fetch_movie_details(movie_id)
    poster_path = details.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w342" + poster_path
    return None

def load_settings():
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print_exception(e)
    return {}

def save_settings(settings):
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print_exception(e)

class ActivityLogTab(QWidget):
    log_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        outer_layout = QVBoxLayout()
        self.label = QLabel("Activity Log:")
        self.label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.label.setStyleSheet("color: #f8f8f8; margin-bottom: 10px;")
        outer_layout.addWidget(self.label)
        self.card = QFrame()
        self.card.setFrameShape(QFrame.StyledPanel)
        self.card.setStyleSheet("""
            QFrame {
                border-radius: 20px;
                background: #232330;
                border: 1.5px solid #31313f;
                padding: 16px;
                margin: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(60, 60, 60, 120))
        self.card.setGraphicsEffect(shadow)
        card_layout = QVBoxLayout(self.card)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 11))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #f0f0f0;
                font-size: 11pt;
                padding: 10px;
            }
        """)
        card_layout.addWidget(self.log_text)
        outer_layout.addWidget(self.card)
        self.setLayout(outer_layout)
        self.log_signal.connect(self.append)
    def append(self, message):
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(message + '\n')
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()
    def clear(self):
        self.log_text.clear()

class MovieListTab(QWidget):
    def __init__(self, movie_list_path):
        super().__init__()
        self.movie_list_path = movie_list_path
        layout = QVBoxLayout()
        label = QLabel("Movie List:")
        label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        layout.addWidget(label)
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #191922;
                border-radius: 10px;
                color: #e0e0e0;
                font-size: 12pt;
                padding: 12px;
                border: 1.5px solid #414151;
            }
        """)
        layout.addWidget(self.text_edit)
        save_btn = QPushButton("💾 Save List")
        save_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                color: #f0f0f0;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #414151, stop:1 #23272a
                );
                border-radius: 13px;
                padding: 9px 26px;
                font-weight: 600;
                margin-top: 10px;
                border: 1px solid #6a7ca3;
            }
            QPushButton:hover {
                background: #2f2f38;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(40, 40, 40, 90))
        save_btn.setGraphicsEffect(shadow)
        save_btn.clicked.connect(self.save_list)
        layout.addWidget(save_btn)
        self.setLayout(layout)
        self.load_list()
    def load_list(self):
        self.text_edit.setText("\n".join(read_file_lines(self.movie_list_path)))
    def save_list(self):
        try:
            lines = self.text_edit.toPlainText().splitlines()
            write_file_lines(self.movie_list_path, lines)
            QMessageBox.information(self, "Saved", "Movie list saved.")
        except Exception as e:
            print_exception(e)
            QMessageBox.critical(self, "Error", f"Could not save: {e}")

class NextUpTab(QWidget):
    def __init__(self, planned, play_callback=None):
        super().__init__()
        self.play_callback = play_callback
        layout = QVBoxLayout()
        header = QHBoxLayout()
        label = QLabel("Next Up:")
        label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        header.addWidget(label)
        header.addStretch()
        layout.addLayout(header)
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Segoe UI", 12))
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #191922;
                border-radius: 9px;
                color: #e0e0e0;
                font-size: 12pt;
                padding: 10px;
                border: 1.5px solid #414151;
            }
        """)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.update_nextup(planned)
        self.list_widget.itemDoubleClicked.connect(self.play_item)
    def update_nextup(self, planned):
        self.list_widget.clear()
        for title in planned[:10]:
            self.list_widget.addItem("🎬 " + title)
    def play_item(self, item):
        if self.play_callback:
            title = item.text().replace("🎬 ", "")
            self.play_callback(title)

class RecommendationsTab(QWidget):
    def __init__(self, processed, collection, gui):
        super().__init__()
        self.processed = set(processed)
        self.collection = set(collection)
        self.genres = tmdb_get_genres()
        self.gui = gui
        layout = QVBoxLayout()
        label = QLabel("Recommendations")
        label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        label.setStyleSheet("color: #f0f0f0; margin-bottom: 7px;")
        layout.addWidget(label)
        filter_layout = QHBoxLayout()
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("Any", "")
        for gid, gname in self.genres.items():
            self.genre_combo.addItem(gname, gid)
        filter_layout.addWidget(QLabel("Genre:"))
        filter_layout.addWidget(self.genre_combo)
        self.year_edit = QLineEdit()
        self.year_edit.setPlaceholderText("Year (optional)")
        filter_layout.addWidget(QLabel("Year:"))
        filter_layout.addWidget(self.year_edit)
        self.language_combo = QComboBox()
        for nation, lang_code in LANGUAGES.items():
            self.language_combo.addItem(nation, lang_code)
        filter_layout.addWidget(QLabel("Nation:"))
        filter_layout.addWidget(self.language_combo)
        self.exclude_mainstream_checkbox = QCheckBox("Exclude Mainstream")
        filter_layout.addWidget(self.exclude_mainstream_checkbox)
        self.curated_combo = QComboBox()
        self.curated_combo.addItem("None", "")
        for label, kid in CURATED_KEYWORDS.items():
            self.curated_combo.addItem(label, kid)
        filter_layout.addWidget(QLabel("Curated:"))
        filter_layout.addWidget(self.curated_combo)
        layout.addLayout(filter_layout)
        btn_layout = QHBoxLayout()
        generate_btn = QPushButton("🔮 Recommend")
        generate_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        generate_btn.clicked.connect(self.generate_recommendations)
        btn_layout.addWidget(generate_btn)
        surprise_btn = QPushButton("🎲 Surprise Me")
        surprise_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        surprise_btn.clicked.connect(self.surprise_me)
        btn_layout.addWidget(surprise_btn)
        btn_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(btn_layout)
        results_layout = QHBoxLayout()
        left_col = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Segoe UI", 12))
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #191922;
                border-radius: 10px;
                color: #f0f0f0;
                font-size: 12pt;
                padding: 10px;
                border: 1.5px solid #414151;
                min-width: 350px;
            }
        """)
        self.list_widget.setMinimumWidth(350)
        self.list_widget.itemClicked.connect(self.on_item_selected)
        self.list_widget.itemDoubleClicked.connect(self.add_to_download_list)
        left_col.addWidget(self.list_widget)
        results_layout.addLayout(left_col)
        poster_col = QVBoxLayout()
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(220, 340)
        self.poster_label.setStyleSheet("background:#222; border-radius:10px; border:1px solid #111; margin-bottom:18px;")
        self.poster_label.setAlignment(Qt.AlignCenter)
        poster_col.addWidget(self.poster_label)
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setTextFormat(Qt.RichText)
        self.desc_label.setStyleSheet("""
            background: #181c23;
            color: #ebebeb;
            font-size: 13px;
            padding: 16px 18px 16px 18px;
            border-radius: 10px;
            margin-top: 10px;
            min-width: 220px;
            max-width: 330px;
        """)
        poster_col.addWidget(self.desc_label)
        poster_col.addStretch()
        results_layout.addLayout(poster_col)
        layout.addLayout(results_layout)
        self.setLayout(layout)
        self.recommendations = []

    def _recommendations_from_tmdb(self, genre_id, year, language, curated_keyword, exclude_mainstream):
        results = []
        base_url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1
        }
        if genre_id:
            params["with_genres"] = genre_id
        if year:
            params["year"] = year
        if language:
            params["with_original_language"] = language
        if curated_keyword:
            params["with_keywords"] = curated_keyword
        if exclude_mainstream:
            params["vote_count.lte"] = 1000
        try:
            resp = requests.get(base_url, params=params, timeout=12)
            data = resp.json()
            for m in data.get("results", []):
                title = m.get("title", "")
                year_val = m.get("release_date", "")[:4] if m.get("release_date") else ""
                movie_id = m.get("id")
                details = tmdb_fetch_movie_details(movie_id)
                overview = details.get("overview", "No description.")
                director = ""
                actors = []
                if details.get("credits"):
                    for c in details["credits"].get("crew", []):
                        if c.get("job") == "Director":
                            director = c.get("name")
                            break
                    actors = [a.get("name") for a in details["credits"].get("cast", [])[:2]]
                full_title = f"{title} ({year_val})" if year_val else title
                desc = ""
                if overview:
                    desc += f"{overview}<br>"
                if director:
                    desc += f"<b>Director:</b> {director}<br>"
                if actors:
                    desc += f"<b>Stars:</b> {', '.join(actors)}"
                results.append((full_title, movie_id, desc))
                if len(results) >= 12:
                    break
        except Exception as e:
            print_exception(e)
        return results

    def generate_recommendations(self):
        genre_id = self.genre_combo.currentData()
        year = self.year_edit.text().strip() if self.year_edit.text().strip() else None
        language = self.language_combo.currentData()
        exclude_mainstream = self.exclude_mainstream_checkbox.isChecked()
        curated_keyword = self.curated_combo.currentData()
        results = self._recommendations_from_tmdb(genre_id, year, language, curated_keyword, exclude_mainstream)
        self.recommendations = results
        self.list_widget.clear()
        self.poster_label.clear()
        self.desc_label.clear()
        for i, (title, movie_id, desc) in enumerate(results):
            self.list_widget.addItem(title)
        if results:
            self.on_item_selected(self.list_widget.item(0))

    def on_item_selected(self, item):
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self.recommendations):
            _, movie_id, desc = self.recommendations[idx]
            poster_url = tmdb_fetch_movie_poster_url(movie_id)
            if poster_url:
                try:
                    resp = requests.get(poster_url, timeout=10)
                    pix = QPixmap()
                    pix.loadFromData(resp.content)
                    self.poster_label.setPixmap(pix.scaled(220, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                except Exception:
                    self.poster_label.clear()
            else:
                self.poster_label.clear()
            self.desc_label.setText(desc)
        else:
            self.poster_label.clear()
            self.desc_label.clear()

    def surprise_me(self):
        genre_id = random.choice(list(self.genres.keys()))
        year = str(random.choice(range(1960, 2024)))
        language = random.choice(list(LANGUAGES.values()))
        self.genre_combo.setCurrentIndex(list(self.genres.keys()).index(genre_id) + 1 if genre_id in self.genres else 0)
        self.year_edit.setText(year)
        idx = list(LANGUAGES.values()).index(language)
        self.language_combo.setCurrentIndex(idx)
        self.generate_recommendations()

    def add_to_download_list(self, item):
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self.recommendations):
            title, _, _ = self.recommendations[idx]
            current_list = read_file_lines(DOWNLOAD_LIST_FILE)
            if title not in current_list:
                current_list.append(title)
                write_file_lines(DOWNLOAD_LIST_FILE, current_list)
                QMessageBox.information(self, "Added", f"{title} added to download list.")
                if hasattr(self.gui, "list_tab"):
                    self.gui.list_tab.load_list()
            else:
                QMessageBox.information(self, "Already Exists", f"{title} is already in download list.")

class TorrentTrackerTab(QWidget):
    def __init__(self, gui=None):
        super().__init__()
        self.gui = gui
        layout = QVBoxLayout()
        label = QLabel("Torrent Tracker:")
        label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        layout.addWidget(label)
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Segoe UI", 11))
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #191922;
                border-radius: 10px;
                color: #e0e0e0;
                font-size: 11pt;
                padding: 8px;
                border: 1.5px solid #414151;
            }
        """)
        layout.addWidget(self.list_widget)
        btn_layout = QHBoxLayout()
        self.pause_btn = QPushButton("⏸ Pause")
        self.resume_btn = QPushButton("▶ Resume")
        self.remove_btn = QPushButton("❌ Remove")
        for b in (self.pause_btn, self.resume_btn, self.remove_btn):
            b.setFont(QFont("Segoe UI", 11, QFont.Bold))
            b.setStyleSheet("QPushButton {border-radius:10px; background:#282838; color:#fafafa; padding:7px 18px;}")
            b.setEnabled(False)
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.selected_hash = None
        self.pause_btn.clicked.connect(self.pause_torrent)
        self.resume_btn.clicked.connect(self.resume_torrent)
        self.remove_btn.clicked.connect(self.remove_torrent)
        self.list_widget.itemClicked.connect(self.select_row)
        self.session = requests.Session()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_torrent_list)
        self.refresh_timer.start(4000)
        self.login_success = False
        self.refresh_torrent_list()

    def set_buttons_enabled(self, enabled):
        self.pause_btn.setEnabled(enabled)
        self.resume_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)

    def qb_login(self):
        if self.login_success:
            return True
        try:
            url = f"http://{QB_HOST}:{QB_PORT}/api/v2/auth/login"
            r = self.session.post(url, data={"username": QB_USER, "password": QB_PASS}, timeout=3)
            if r.text == "Ok." or r.text == "Ok":
                self.login_success = True
                return True
            else:
                print(f"qB login failed: {r.text}")
        except Exception as e:
            print_exception(e)
        return False

    def refresh_torrent_list(self):
        self.list_widget.clear()
        self.hashes = []
        self.selected_hash = None
        self.set_buttons_enabled(False)
        if not self.qb_login():
            self.list_widget.addItem("Could not connect to qBittorrent WebUI.")
            return
        try:
            url = f"http://{QB_HOST}:{QB_PORT}/api/v2/torrents/info"
            r = self.session.get(url, timeout=5)
            if r.status_code == 200:
                torrents = r.json()
                for t in torrents:
                    name = t.get("name", "Unknown")
                    progress = t.get("progress", 0)
                    state = t.get("state", "unknown")
                    hash_ = t.get("hash", "")
                    msg = f"{name} | {int(progress*100)}% | {state}"
                    item = QListWidgetItem(msg)
                    item.setData(Qt.UserRole, hash_)
                    self.list_widget.addItem(item)
                    self.hashes.append(hash_)
            else:
                self.list_widget.addItem("Error fetching torrent list.")
        except Exception as e:
            print_exception(e)
            self.list_widget.addItem("Error fetching torrent list.")

    def select_row(self, item):
        self.selected_hash = item.data(Qt.UserRole)
        self.set_buttons_enabled(True)

    def pause_torrent(self):
        if not self.selected_hash:
            QMessageBox.information(self, "Pause", "Select a torrent first.")
            return
        if not self.qb_login():
            QMessageBox.warning(self, "Pause", "Not connected to qBittorrent.")
            return
        try:
            url = f"http://{QB_HOST}:{QB_PORT}/api/v2/torrents/pause"
            r = self.session.post(url, data={"hashes": self.selected_hash}, timeout=5)
            self.refresh_torrent_list()
            self.selected_hash = None
            self.set_buttons_enabled(False)
        except Exception as e:
            print_exception(e)
            QMessageBox.critical(self, "Pause Error", str(e))

    def resume_torrent(self):
        if not self.selected_hash:
            QMessageBox.information(self, "Resume", "Select a torrent first.")
            return
        if not self.qb_login():
            QMessageBox.warning(self, "Resume", "Not connected to qBittorrent.")
            return
        try:
            url = f"http://{QB_HOST}:{QB_PORT}/api/v2/torrents/resume"
            r = self.session.post(url, data={"hashes": self.selected_hash}, timeout=5)
            self.refresh_torrent_list()
            self.selected_hash = None
            self.set_buttons_enabled(False)
        except Exception as e:
            print_exception(e)
            QMessageBox.critical(self, "Resume Error", str(e))

    def remove_torrent(self):
        if not self.selected_hash:
            QMessageBox.information(self, "Remove", "Select a torrent first.")
            return
        if not self.qb_login():
            QMessageBox.warning(self, "Remove", "Not connected to qBittorrent.")
            return
        try:
            url = f"http://{QB_HOST}:{QB_PORT}/api/v2/torrents/delete"
            r = self.session.post(url, data={"hashes": self.selected_hash, "deleteFiles": "true"}, timeout=5)
            self.refresh_torrent_list()
            self.selected_hash = None
            self.set_buttons_enabled(False)
        except Exception as e:
            print_exception(e)
            QMessageBox.critical(self, "Remove Error", str(e))

class SettingsTab(QWidget):
    def __init__(self, gui=None):
        super().__init__()
        self.gui = gui
        layout = QVBoxLayout()
        label = QLabel("Settings")
        label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        label.setStyleSheet("color: #f0f0f0; margin-bottom: 10px;")
        layout.addWidget(label)

        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Save Folder")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.pick_folder)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)

        self.max_torrents_spin = QSpinBox()
        self.max_torrents_spin.setMinimum(1)
        self.max_torrents_spin.setMaximum(10)
        max_label = QLabel("Max Active Torrents:")
        max_layout = QHBoxLayout()
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.max_torrents_spin)
        layout.addLayout(max_layout)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        s = load_settings()
        if s.get("save_path"):
            self.folder_edit.setText(s["save_path"])
        elif hasattr(self.gui, "save_path"):
            self.folder_edit.setText(self.gui.save_path)
        if s.get("max_active_torrents"):
            self.max_torrents_spin.setValue(s["max_active_torrents"])
        elif hasattr(self.gui, "max_active_torrents"):
            self.max_torrents_spin.setValue(self.gui.max_active_torrents)

    def save_settings(self):
        s = {
            "save_path": self.folder_edit.text(),
            "max_active_torrents": self.max_torrents_spin.value()
        }
        save_settings(s)
        if self.gui:
            self.gui.save_path = self.folder_edit.text()
            self.gui.max_active_torrents = self.max_torrents_spin.value()
            self.gui.folder_label.setText(f"Save Folder: {self.gui.save_path}")
        QMessageBox.information(self, "Settings", "Settings saved.")

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.folder_edit.setText(folder)

class LeopoldsVaultGUI(QWidget):
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
    def tab_changed(self, idx):
        tab_name = self.tabs.tabText(idx)
        if tab_name == "Movie List":
            self.list_tab.load_list()
        elif tab_name == "Next Up":
            self.nextup_tab.update_nextup(self.planned)
        elif tab_name == "Torrent Tracker":
            self.torrent_tab.refresh_torrent_list()
        elif tab_name == "Settings":
            self.settings_tab.load_settings()
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.save_path = folder
            self.folder_label.setText(f"Save Folder: {folder}")
    def start_download(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.activity_tab.clear()
        python_path = sys.executable
        downloader_path = os.path.join(os.path.dirname(sys.argv[0]), "movie_downloader2.py")
        env = os.environ.copy()
        env["DOWNLOAD_PATH"] = self.save_path
        env["MAX_ACTIVE_TORRENTS"] = str(self.max_active_torrents)
        planned = set(read_file_lines(DOWNLOAD_LIST_FILE))
        processed = set(read_file_lines(PROCESSED_MOVIES_FILE))
        collection = set([c.split(" (")[0] for c in read_file_lines(COLLECTION_FILE)])
        to_download = list(planned - processed - collection)
        temp_download_file = "filtered_download_list.txt"
        write_file_lines(temp_download_file, to_download)
        env["DOWNLOAD_LIST_FILE"] = temp_download_file
        self.process = subprocess.Popen(
            [python_path, downloader_path] + to_download,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )
        threading.Thread(target=self.update_log_and_progress, daemon=True).start()
    def update_log_and_progress(self):
        for line in self.process.stdout:
            if line.strip():
                self.activity_tab.log_signal.emit(line.strip())
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def stop_download(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.activity_tab.log_signal.emit("Download stopped by user.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def play_nextup(self, movie_title):
        possible = [f for f in os.listdir(self.save_path) if movie_title.split(" (")[0] in f]
        if possible:
            file = os.path.join(self.save_path, possible[0])
            try:
                if sys.platform == "win32":
                    os.startfile(file)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", file])
                else:
                    subprocess.Popen(["xdg-open", file])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open: {e}")
        else:
            QMessageBox.information(self, "File Not Found", f"No file for '{movie_title}' found in {self.save_path}.")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        gui = LeopoldsVaultGUI()
        gui.show()
        sys.exit(app.exec_())
    except Exception as e:
        print_exception(e)