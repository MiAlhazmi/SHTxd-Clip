"""
Self-updating mechanism for yt-dlp in bundled executables
Downloads and replaces yt-dlp files automatically
"""

import os
import sys
import json
import shutil
import tempfile
import requests
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional

class YtDlpUpdater:
    """Handles yt-dlp self-updating in executable environment"""
    
    def __init__(self):
        self.callbacks = {}
        self.yt_dlp_github_api = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        
        # Determine if running as executable
        if getattr(sys, 'frozen', False):
            # Running as executable
            self.is_executable = True
            self.app_dir = Path(sys._MEIPASS)
            self.yt_dlp_dir = self.app_dir / "yt_dlp"
            # User data directory for updates
            self.user_data_dir = Path.home() / ".shtxd_clip"
            self.user_data_dir.mkdir(exist_ok=True)
            self.yt_dlp_backup_dir = self.user_data_dir / "yt_dlp_backup"
        else:
            # Running as script
            self.is_executable = False
            self.app_dir = Path(__file__).parent
            self.yt_dlp_dir = None
            self.user_data_dir = None
            self.yt_dlp_backup_dir = None
    
    def set_callbacks(self, callbacks: Dict[str, Any]):
        """Set callback functions for UI updates"""
        self.callbacks = callbacks
    
    def _log(self, message: str):
        """Send log message to UI"""
        if 'on_log' in self.callbacks:
            self.callbacks['on_log'](message)
        print(message)
    
    def get_current_version(self) -> Optional[str]:
        """Get current yt-dlp version"""
        try:
            import yt_dlp
            return yt_dlp.version.__version__
        except:
            return None
    
    def get_latest_version(self) -> Optional[Dict[str, Any]]:
        """Get latest yt-dlp version from GitHub"""
        try:
            self._log("🔍 Checking for yt-dlp updates...")
            response = requests.get(self.yt_dlp_github_api, timeout=10)
            
            if response.status_code == 200:
                release_data = response.json()
                return {
                    'version': release_data['tag_name'],
                    'download_url': self.get_download_url(release_data),
                    'published_at': release_data['published_at']
                }
            return None
        except Exception as e:
            self._log(f"❌ Error checking for updates: {e}")
            return None
    
    def get_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """Get the appropriate download URL for yt-dlp"""
        # Look for the source code zip
        for asset in release_data.get('assets', []):
            if 'yt-dlp' in asset['name'] and asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        
        # Fallback to zipball_url
        return release_data.get('zipball_url')
    
    def needs_update(self) -> bool:
        """Check if yt-dlp needs updating"""
        if not self.is_executable:
            return False
            
        current = self.get_current_version()
        latest_info = self.get_latest_version()
        
        if not current or not latest_info:
            return False
        
        latest = latest_info['version'].lstrip('v')
        
        # Simple version comparison
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad with zeros
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_and_extract(self, download_url: str) -> bool:
        """Download and extract yt-dlp update"""
        try:
            self._log("📥 Downloading yt-dlp update...")
            
            # Download to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        self._log(f"📥 Downloading: {progress:.1f}%")
                
                temp_zip_path = temp_file.name
            
            # Extract to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                self._log("📦 Extracting update...")
                
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find yt_dlp folder in extracted files
                temp_path = Path(temp_dir)
                yt_dlp_source = None
                
                # Look for yt_dlp folder
                for item in temp_path.rglob('yt_dlp'):
                    if item.is_dir() and (item / '__init__.py').exists():
                        yt_dlp_source = item
                        break
                
                if not yt_dlp_source:
                    self._log("❌ Could not find yt_dlp folder in update")
                    return False
                
                # Create backup of current yt-dlp
                if self.yt_dlp_dir.exists():
                    self._log("💾 Creating backup...")
                    if self.yt_dlp_backup_dir.exists():
                        shutil.rmtree(self.yt_dlp_backup_dir)
                    shutil.copytree(self.yt_dlp_dir, self.yt_dlp_backup_dir)
                
                # Copy new yt-dlp files
                self._log("🔄 Installing update...")
                if self.yt_dlp_dir.exists():
                    shutil.rmtree(self.yt_dlp_dir)
                
                shutil.copytree(yt_dlp_source, self.yt_dlp_dir)
                
                # Clean up temp file
                os.unlink(temp_zip_path)
                
                self._log("✅ yt-dlp updated successfully!")
                return True
                
        except Exception as e:
            self._log(f"❌ Update failed: {e}")
            # Restore backup if it exists
            if hasattr(self, 'yt_dlp_backup_dir') and self.yt_dlp_backup_dir.exists():
                self._log("🔄 Restoring backup...")
                if self.yt_dlp_dir.exists():
                    shutil.rmtree(self.yt_dlp_dir)
                shutil.copytree(self.yt_dlp_backup_dir, self.yt_dlp_dir)
            return False
    
    def update_yt_dlp(self) -> bool:
        """Main update method"""
        if not self.is_executable:
            self._log("ℹ️ Manual yt-dlp update not needed in development mode")
            return True
        
        self._log("🔄 Checking for yt-dlp updates...")
        
        latest_info = self.get_latest_version()
        if not latest_info:
            self._log("❌ Could not check for updates")
            return False
        
        current_version = self.get_current_version()
        latest_version = latest_info['version'].lstrip('v')
        
        self._log(f"📊 Current version: {current_version}")
        self._log(f"📊 Latest version: {latest_version}")
        
        if not self.needs_update():
            self._log("✅ yt-dlp is already up to date")
            return True
        
        # Perform update
        download_url = latest_info['download_url']
        if not download_url:
            self._log("❌ No download URL found")
            return False
        
        return self.download_and_extract(download_url)
    
    def auto_update_check(self) -> bool:
        """Check for updates automatically (silent)"""
        if not self.is_executable:
            return True
            
        try:
            if self.needs_update():
                self._log("🔄 Auto-updating yt-dlp...")
                return self.update_yt_dlp()
            return True
        except Exception as e:
            self._log(f"⚠️ Auto-update check failed: {e}")
            return True  # Don't fail the app if auto-update fails
