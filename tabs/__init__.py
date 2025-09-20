"""
Tabs package for Leopold's Vault GUI application.
"""

from .activity_log_tab import ActivityLogTab
from .movie_list_tab import MovieListTab
from .nextup_tab import NextUpTab
from .torrent_tracker_tab import TorrentTrackerTab
from .settings_tab import SettingsTab
from .recommendations_tab import RecommendationsTab

__all__ = [
    "ActivityLogTab",
    "MovieListTab", 
    "NextUpTab",
    "TorrentTrackerTab",
    "SettingsTab",
    "RecommendationsTab"
]
