"""
Configuration file for SHTxd Clip
Contains all constants, settings, and configuration data
"""

from pathlib import Path
import re

# Application Info
APP_NAME = "SHTxd Clip"
APP_VERSION = "1.0.0"
GITHUB_REPO = "mialhazmi/shtxd-clip"  # Your repo
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
APP_AUTHOR = "ShortaXD"

# Window Configuration
DEFAULT_WINDOW_SIZE = "900x750"
MIN_WINDOW_SIZE = (650, 500)

# File Paths
HOME_DIR = Path.home()
SETTINGS_FILE = HOME_DIR / ".yt_downloader_settings.json"
HISTORY_FILE = HOME_DIR / ".yt_downloader_history.json"
DEFAULT_DOWNLOAD_PATH = HOME_DIR / "Downloads"

# Download Configuration
MAX_HISTORY_ENTRIES = 50
DEFAULT_QUALITY = "best"
DEFAULT_THEME = "dark"

# Quality Options
QUALITY_OPTIONS = [
    {
        "value": "best",
        "name": "Best Quality (MP4)",
        "description": "Highest resolution available",
        "icon": "🎬",
        "colors": ["#4CAF50", "#388E3C"]
    },
    {
        "value": "1080p", 
        "name": "Full HD (1080p)",
        "description": "1920x1080 resolution",
        "icon": "📺",
        "colors": ["#2196F3", "#1976D2"]
    },
    {
        "value": "720p",
        "name": "HD (720p)", 
        "description": "1280x720 resolution",
        "icon": "📹",
        "colors": ["#FF9800", "#F57C00"]
    },
    {
        "value": "worst",
        "name": "Low Quality",
        "description": "Smallest file size", 
        "icon": "📱",
        "colors": ["#795548", "#5D4037"]
    },
    {
        "value": "audio",
        "name": "MP3 Audio Only",
        "description": "Best audio quality",
        "icon": "🎵", 
        "colors": ["#9C27B0", "#7B1FA2"]
    }
]

# Advanced Options
ADVANCED_OPTIONS = [
    {
        "key": "playlist",
        "text": "📁 Download entire playlist",
        "description": "Download all videos in the playlist"
    },
    {
        "key": "subtitles", 
        "text": "📝 Download subtitles",
        "description": "Include subtitle files"
    },
    {
        "key": "thumbnail",
        "text": "🖼️ Download thumbnail", 
        "description": "Save video thumbnail image"
    }
]

# Playlist Options
PLAYLIST_QUANTITY_OPTIONS = ["5", "10", "20", "50", "All"]
DEFAULT_PLAYLIST_QUANTITY = "10"

# URL Validation Patterns
YOUTUBE_URL_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
    r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+', 
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
    r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
    r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+'
]

# Progress Parsing Patterns
PROGRESS_PATTERNS = {
    'percentage': r'(\d+(?:\.\d+)?)%',
    'speed': r'(\d+(?:\.\d+)?[KMG]?iB/s)',
    'eta': r'ETA (\S+)'
}

# UI Colors and Styling
UI_COLORS = {
    'primary': ["#2196F3", "#1976D2"],
    'secondary': ["#607D8B", "#455A64"], 
    'success': ["#4CAF50", "#388E3C"],
    'warning': ["#FF9800", "#F57C00"],
    'danger': ["#FF5722", "#D84315"],
    'cancel': ["#d32f2f", "#f44336"],
    'border': ["#e0e0e0", "#404040"]
}

# Font Configuration
FONTS = {
    'title': {'size': 28, 'weight': 'bold'},
    'section_header': {'size': 16, 'weight': 'bold'},
    'button': {'size': 16, 'weight': 'bold'},
    'label': {'size': 13, 'weight': 'bold'},
    'text': {'size': 12},
    'small': {'size': 11},
    'tiny': {'size': 10},
    'log': {'family': 'SF Mono', 'size': 11}
}

# Timeouts and Delays
TIMEOUTS = {
    'video_info': 30,
    'playlist_info': 30, 
    'update_check': 10,
    'update_install': 30
}

# Log Messages
LOG_MESSAGES = {
    'app_ready': "🎬 SHTxd Clip ready! Paste a URL and click Preview to get started.",
    'ui_loaded': "✨ Enhanced UI loaded successfully!",
    'download_start': "🚀 Starting download...",
    'download_complete': "✅ Download completed successfully!",
    'download_cancelled': "🛑 Download cancelled by user",
    'log_cleared': "📝 Log cleared",
    'history_cleared': "🗑️ Download history cleared",
    'ready_next': "🔄 Ready for next download"
}

# Error Messages
ERROR_MESSAGES = {
    'missing_url': "Please enter a YouTube video URL!",
    'invalid_url': "Please enter a valid YouTube URL!",
    'missing_deps': "Missing dependencies: {deps}\n\nPlease install:\n{install_instructions}",
    'path_error': "Cannot create download directory:\n{error}",
    'yt_dlp_not_found': "yt-dlp is not installed or not found in PATH.\n\nInstall with: pip install yt-dlp"
}

# Dependencies
REQUIRED_DEPENDENCIES = {
    'yt-dlp': 'pip install yt-dlp',
    'ffmpeg': 'Download from https://ffmpeg.org/'
}

# CustomTkinter Configuration
CTK_CONFIG = {
    'appearance_mode': 'dark',
    'color_theme': 'blue'
}
