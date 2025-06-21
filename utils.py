"""
Utility functions for SHTxd Clip
Handles settings, history, validation, and other helper functions
"""

import json
import re
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import config

class SettingsManager:
    """Manages application settings persistence"""
    
    def __init__(self):
        self.settings_file = config.SETTINGS_FILE
        self.default_settings = {
            'download_path': str(config.DEFAULT_DOWNLOAD_PATH),
            'theme': config.DEFAULT_THEME,
            'default_quality': config.DEFAULT_QUALITY,
            'window_geometry': config.DEFAULT_WINDOW_SIZE,
            'playlist_quantity': config.DEFAULT_PLAYLIST_QUANTITY
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file, return defaults if file doesn't exist"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.default_settings, **settings}
            return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

class HistoryManager:
    """Manages download history persistence"""
    
    def __init__(self):
        self.history_file = config.HISTORY_FILE
        self.max_entries = config.MAX_HISTORY_ENTRIES
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load download history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading history: {e}")
            return []
    
    def save_history(self, history: List[Dict[str, Any]]) -> bool:
        """Save download history to file"""
        try:
            # Keep only last N entries
            history = history[-self.max_entries:]
            
            # Ensure directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def add_entry(self, history: List[Dict[str, Any]], title: str, url: str, 
                  quality: str, file_path: str) -> List[Dict[str, Any]]:
        """Add new entry to history"""
        entry = {
            'title': title,
            'url': url,
            'quality': quality,
            'path': file_path,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'completed'
        }
        history.append(entry)
        return history
    
    def clear_history(self) -> bool:
        """Clear all history"""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False

class URLValidator:
    """Validates and analyzes YouTube URLs"""
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """Check if URL is a valid YouTube URL"""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        return any(re.match(pattern, url) for pattern in config.YOUTUBE_URL_PATTERNS)
    
    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """Check if URL is a playlist URL"""
        if not url:
            return False
        return "playlist?list=" in url or "&list=" in url
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL"""
        match = re.search(r'list=([^&\n?#]+)', url)
        return match.group(1) if match else None

class DependencyChecker:
    """Checks for required system dependencies"""
    
    @staticmethod
    def check_dependency(command: str) -> bool:
        """Check if a command-line tool is available"""
        try:
            # Use 'where' on Windows, 'which' on Unix-like systems
            check_cmd = 'where' if sys.platform == 'win32' else 'which'
            result = subprocess.run([check_cmd, command], 
                                   capture_output=True, 
                                   text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def check_all_dependencies() -> Dict[str, bool]:
        """Check all required dependencies"""
        results = {}
        for dep in config.REQUIRED_DEPENDENCIES:
            results[dep] = DependencyChecker.check_dependency(dep)
        return results
    
    @staticmethod
    def get_missing_dependencies() -> List[str]:
        """Get list of missing dependencies"""
        results = DependencyChecker.check_all_dependencies()
        return [dep for dep, available in results.items() if not available]
    
    @staticmethod
    def format_dependency_error(missing_deps: List[str]) -> str:
        """Format error message for missing dependencies"""
        install_instructions = []
        for dep in missing_deps:
            if dep in config.REQUIRED_DEPENDENCIES:
                install_instructions.append(f"• {dep}: {config.REQUIRED_DEPENDENCIES[dep]}")
        
        return config.ERROR_MESSAGES['missing_deps'].format(
            deps=', '.join(missing_deps),
            install_instructions='\n'.join(install_instructions)
        )

class ProgressParser:
    """Parses yt-dlp output for progress information"""
    
    @staticmethod
    def parse_progress(line: str) -> Optional[Dict[str, Any]]:
        """Parse a line of yt-dlp output for progress info"""
        if not line or "[download]" not in line:
            return None
        
        progress_info = {}
        
        # Extract percentage
        percent_match = re.search(config.PROGRESS_PATTERNS['percentage'], line)
        if percent_match:
            progress_info['percentage'] = float(percent_match.group(1))
        
        # Extract speed
        speed_match = re.search(config.PROGRESS_PATTERNS['speed'], line)
        if speed_match:
            progress_info['speed'] = speed_match.group(1)
        
        # Extract ETA
        eta_match = re.search(config.PROGRESS_PATTERNS['eta'], line)
        if eta_match:
            progress_info['eta'] = eta_match.group(1)
        
        # Determine status
        if "%" in line:
            progress_info['status'] = 'downloading'
        elif "Destination:" in line:
            progress_info['status'] = 'preparing'
            # Extract file path
            try:
                file_path = line.split("[download] Destination: ")[1]
                progress_info['file_path'] = file_path
            except IndexError:
                pass
        elif "already been downloaded" in line:
            progress_info['status'] = 'exists'
        
        return progress_info if progress_info else None
    
    @staticmethod
    def parse_status(line: str) -> Optional[str]:
        """Parse line for status updates"""
        line = line.lower()
        
        if "merging formats" in line:
            return "Merging video and audio..."
        elif "extractaudio" in line:
            return "Extracting audio..."
        elif "downloading webpage" in line:
            return "Fetching video information..."
        elif "downloading tv client config" in line:
            return "Loading video data..."
        
        return None

class FileManager:
    """Handles file and directory operations"""
    
    @staticmethod
    def ensure_directory_exists(path: str) -> bool:
        """Ensure directory exists, create if needed"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Could not create directory {path}: {e}")
            return False
    
    @staticmethod
    def open_folder(path: str) -> bool:
        """Open folder in system file manager"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
            return True
        except Exception as e:
            print(f"Could not open folder {path}: {e}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Convert filename to safe format"""
        # Remove or replace unsafe characters
        unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        safe_filename = filename
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Limit length
        if len(safe_filename) > 255:
            safe_filename = safe_filename[:255]
        
        return safe_filename.strip()

class Logger:
    """Simple logging utility with timestamp"""
    
    @staticmethod
    def format_message(message: str) -> str:
        """Format message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {message}"
    
    @staticmethod
    def get_log_message(key: str) -> str:
        """Get predefined log message"""
        return config.LOG_MESSAGES.get(key, f"Unknown log message: {key}")

class ThemeManager:
    """Manages application theming"""
    
    @staticmethod
    def apply_theme(theme: str) -> bool:
        """Apply theme to CustomTkinter"""
        try:
            import customtkinter as ctk
            ctk.set_appearance_mode(theme)
            return True
        except Exception as e:
            print(f"Error applying theme {theme}: {e}")
            return False
    
    @staticmethod
    def get_available_themes() -> List[str]:
        """Get list of available themes"""
        return ["dark", "light", "system"]

# Utility Functions
def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human readable format"""
    if not bytes_size:
        return "Unknown"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

def truncate_text(text: str, max_length: int = 60) -> str:
    """Truncate text to max length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


class GitHubUpdater:
    """Handles checking and downloading updates from GitHub releases"""

    def __init__(self):
        self.repo = config.GITHUB_REPO
        self.api_url = config.UPDATE_CHECK_URL
        self.current_version = config.APP_VERSION

    def check_for_updates(self) -> Dict[str, Any]:
        """Check GitHub for latest release"""
        try:
            import requests
            response = requests.get(self.api_url, timeout=10)

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name'].lstrip('v')

                if self.is_newer_version(latest_version):
                    return {
                        'update_available': True,
                        'latest_version': latest_version,
                        'download_url': self.get_installer_url(release_data),
                        'release_notes': release_data.get('body', ''),
                        'release_date': release_data.get('published_at', ''),
                        'release_name': release_data.get('name', f'Version {latest_version}')
                    }

            return {'update_available': False}

        except Exception as e:
            return {'update_available': False, 'error': str(e)}

    def is_newer_version(self, latest_version: str) -> bool:
        """Compare version numbers (simple comparison)"""
        try:
            # Remove 'v' prefix if present and split
            current = [int(x) for x in self.current_version.lstrip('v').split('.')]
            latest = [int(x) for x in latest_version.lstrip('v').split('.')]

            # Pad with zeros if lengths don't match
            max_len = max(len(current), len(latest))
            current.extend([0] * (max_len - len(current)))
            latest.extend([0] * (max_len - len(latest)))

            return latest > current
        except:
            return False

    def get_installer_url(self, release_data: Dict) -> Optional[str]:
        """Find the installer download URL from release assets"""
        for asset in release_data.get('assets', []):
            name = asset['name'].lower()
            # Look for Windows installer or portable version
            if name.endswith('.exe') or 'setup' in name or 'installer' in name:
                return asset['browser_download_url']
        return None

    def download_update(self, download_url: str, save_path: str) -> bool:
        """Download update file"""
        try:
            import requests
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
