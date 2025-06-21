"""
Core functionality for YouTube Downloader Pro
Handles all download logic, playlist processing, and yt-dlp integration
"""

import subprocess
import threading
import json
import time
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import config
from utils import URLValidator, ProgressParser, FileManager, Logger

class VideoInfo:
    """Container for video information"""
    
    def __init__(self, data: Dict[str, Any]):
        self.raw_data = data
        self.title = data.get('title', 'Unknown Title')
        self.uploader = data.get('uploader', 'Unknown Channel')
        self.duration = data.get('duration', 0)
        self.view_count = data.get('view_count', 0)
        self.upload_date = data.get('upload_date', '')
        self.description = data.get('description', '')
        self.thumbnail_url = data.get('thumbnail', '')
        self.video_id = data.get('id', '')
        self.url = data.get('webpage_url', '')
    
    def get_formatted_duration(self) -> str:
        """Get duration in MM:SS format"""
        if not self.duration:
            return "Unknown"
        return f"{self.duration // 60}:{self.duration % 60:02d}"
    
    def get_formatted_upload_date(self) -> str:
        """Get upload date in YYYY-MM-DD format"""
        if not self.upload_date or len(self.upload_date) < 8:
            return "Unknown"
        return f"{self.upload_date[:4]}-{self.upload_date[4:6]}-{self.upload_date[6:8]}"
    
    def get_formatted_view_count(self) -> str:
        """Get view count with thousands separators"""
        if not self.view_count:
            return "Unknown"
        return f"{self.view_count:,}"

class PlaylistInfo:
    """Container for playlist information"""
    
    def __init__(self, videos: List[Dict[str, Any]]):
        self.videos = videos
        self.total_count = len(videos)
        self.total_duration = self._calculate_total_duration()
        self.estimated_duration = self._estimate_total_duration()
    
    def _calculate_total_duration(self) -> int:
        """Calculate total duration of videos with known durations"""
        total = 0
        for video in self.videos:
            duration = video.get('duration', 0)
            if duration:
                total += duration
        return total
    
    def _estimate_total_duration(self) -> int:
        """Estimate total duration for all videos"""
        videos_with_duration = [v for v in self.videos if v.get('duration')]
        if not videos_with_duration:
            return 0
        
        avg_duration = self.total_duration / len(videos_with_duration)
        return int(avg_duration * self.total_count)
    
    def get_preview_titles(self, count: int = 3) -> List[str]:
        """Get first N video titles for preview"""
        titles = []
        for i, video in enumerate(self.videos[:count]):
            title = video.get('title', f'Video {i + 1}')
            titles.append(title)
        return titles
    
    def get_formatted_duration(self) -> str:
        """Get formatted duration string"""
        if self.estimated_duration == 0:
            return "Duration unknown"
        
        hours = self.estimated_duration // 3600
        minutes = (self.estimated_duration % 3600) // 60
        
        if hours > 0:
            return f"~{hours}h {minutes}m"
        else:
            return f"~{minutes}m"

class DownloadOptions:
    """Container for download options"""
    
    def __init__(self):
        self.quality = "best"
        self.download_playlist = False
        self.playlist_start = 1
        self.playlist_end = 10
        self.playlist_quantity = "10"
        self.download_subtitles = False
        self.download_thumbnail = False
        self.output_path = str(config.DEFAULT_DOWNLOAD_PATH)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'quality': self.quality,
            'download_playlist': self.download_playlist,
            'playlist_start': self.playlist_start,
            'playlist_end': self.playlist_end,
            'playlist_quantity': self.playlist_quantity,
            'download_subtitles': self.download_subtitles,
            'download_thumbnail': self.download_thumbnail,
            'output_path': self.output_path
        }

class DownloadEngine:
    """Main download engine using yt-dlp"""
    
    def __init__(self):
        self.current_process: Optional[subprocess.Popen] = None
        self.is_downloading = False
        self.cancel_requested = False
        self.callbacks: Dict[str, Callable] = {}
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set callback functions for UI updates"""
        self.callbacks = callbacks
    
    def _log(self, message: str):
        """Send log message to UI"""
        if 'on_log' in self.callbacks:
            self.callbacks['on_log'](message)
    
    def _update_progress(self, progress_data: Dict[str, Any]):
        """Send progress update to UI"""
        if 'on_progress' in self.callbacks:
            self.callbacks['on_progress'](progress_data)
    
    def _on_complete(self, success: bool, data: Dict[str, Any]):
        """Send completion status to UI"""
        if 'on_complete' in self.callbacks:
            self.callbacks['on_complete'](success, data)
    
    def _on_error(self, error: str):
        """Send error to UI"""
        if 'on_error' in self.callbacks:
            self.callbacks['on_error'](error)
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information using yt-dlp"""
        try:
            self._log("🔄 Fetching video information...")
            
            cmd = ['yt-dlp', '--dump-json', '--no-download', url]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=config.TIMEOUTS['video_info']
            )
            
            if result.returncode == 0:
                video_data = json.loads(result.stdout.strip().split('\n')[0])
                self._log("✅ Video information loaded")
                return VideoInfo(video_data)
            else:
                self._log(f"❌ Could not fetch video information: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self._log("❌ Request timed out while fetching video info")
            return None
        except json.JSONDecodeError as e:
            self._log(f"❌ Error parsing video information: {e}")
            return None
        except Exception as e:
            self._log(f"❌ Unexpected error: {e}")
            return None
    
    def get_playlist_info(self, url: str) -> Optional[PlaylistInfo]:
        """Get playlist information using yt-dlp"""
        try:
            self._log("🔄 Analyzing playlist...")
            
            cmd = ['yt-dlp', '--flat-playlist', '--dump-json', '--quiet', url]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.TIMEOUTS['playlist_info']
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                playlist_data = []
                
                for line in lines:
                    if line.strip():
                        try:
                            video_info = json.loads(line)
                            playlist_data.append(video_info)
                        except json.JSONDecodeError:
                            continue
                
                if playlist_data:
                    playlist_info = PlaylistInfo(playlist_data)
                    self._log(f"✅ Playlist analyzed: {playlist_info.total_count} videos")
                    return playlist_info
                else:
                    self._log("❌ No videos found in playlist")
                    return None
            else:
                self._log(f"❌ Could not fetch playlist information: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self._log("❌ Request timed out while fetching playlist info")
            return None
        except Exception as e:
            self._log(f"❌ Error fetching playlist: {e}")
            return None
    
    def _build_command(self, url: str, options: DownloadOptions) -> List[str]:
        """Build yt-dlp command based on options"""
        cmd = ["yt-dlp"]
        
        # Quality selection
        if options.quality == "best":
            cmd.extend(["-f", "bv*+ba[ext=m4a]/best[ext=mp4]", "--merge-output-format", "mp4"])
        elif options.quality == "1080p":
            cmd.extend(["-f", "bv*[height<=1080]+ba[ext=m4a]/best[height<=1080]", "--merge-output-format", "mp4"])
        elif options.quality == "720p":
            cmd.extend(["-f", "bv*[height<=720]+ba[ext=m4a]/best[height<=720]", "--merge-output-format", "mp4"])
        elif options.quality == "worst":
            cmd.extend(["-f", "worst[ext=mp4]"])
        elif options.quality == "audio":
            cmd.extend(["-f", "bestaudio", "--extract-audio", "--audio-format", "mp3"])
        
        # Playlist handling
        if options.download_playlist:
            if options.playlist_quantity == "All":
                # Download all videos - no additional flags needed
                pass
            else:
                # Handle quantity or range
                try:
                    if options.playlist_start and options.playlist_end:
                        if options.playlist_start <= options.playlist_end:
                            cmd.extend(["--playlist-start", str(options.playlist_start)])
                            cmd.extend(["--playlist-end", str(options.playlist_end)])
                        else:
                            # Fallback to quantity
                            if options.playlist_quantity.isdigit():
                                cmd.extend(["--playlist-end", options.playlist_quantity])
                    elif options.playlist_quantity.isdigit():
                        cmd.extend(["--playlist-end", options.playlist_quantity])
                except:
                    # Fallback
                    if options.playlist_quantity.isdigit():
                        cmd.extend(["--playlist-end", options.playlist_quantity])
        else:
            cmd.append("--no-playlist")
        
        # Subtitles
        if options.download_subtitles:
            cmd.extend(["--write-subs", "--write-auto-subs", "--sub-lang", "en"])
        
        # Thumbnail
        if options.download_thumbnail:
            cmd.append("--write-thumbnail")
        
        # Output template
        output_template = f"{options.output_path}/%(uploader)s - %(title)s.%(ext)s"
        cmd.extend(["-o", output_template])
        
        # Additional options
        cmd.extend([
            "--ignore-errors",
            "--no-warnings"
        ])
        
        cmd.append(url)
        return cmd
    
    def download(self, url: str, options: DownloadOptions) -> bool:
        """Start download process"""
        if self.is_downloading:
            self._log("❌ Download already in progress")
            return False
        
        # Validate URL
        if not URLValidator.is_valid_youtube_url(url):
            self._on_error("Invalid YouTube URL")
            return False
        
        # Ensure output directory exists
        if not FileManager.ensure_directory_exists(options.output_path):
            self._on_error(f"Could not create output directory: {options.output_path}")
            return False
        
        # Start download in separate thread
        self.is_downloading = True
        self.cancel_requested = False
        
        thread = threading.Thread(
            target=self._download_worker,
            args=(url, options),
            daemon=True
        )
        thread.start()
        return True
    
    def _download_worker(self, url: str, options: DownloadOptions):
        """Worker thread for download process"""
        downloaded_files = []
        
        try:
            # Build command
            cmd = self._build_command(url, options)
            self._log("🚀 Starting download...")
            self._log(f"Command: {' '.join(cmd[:5])}...")
            
            # Start process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Process output
            for line in self.current_process.stdout:
                # Check for cancellation
                if self.cancel_requested:
                    self.current_process.terminate()
                    self._log("🛑 Download cancelled by user")
                    self._on_complete(False, {'reason': 'cancelled'})
                    return
                
                line = line.strip()
                if line:
                    self._log(line)
                    
                    # Parse progress
                    progress_data = ProgressParser.parse_progress(line)
                    if progress_data:
                        self._update_progress(progress_data)
                        
                        # Track downloaded files
                        if 'file_path' in progress_data:
                            downloaded_files.append(progress_data['file_path'])
                    
                    # Parse status updates
                    status = ProgressParser.parse_status(line)
                    if status:
                        self._update_progress({'status_text': status})
            
            # Wait for completion
            return_code = self.current_process.wait()
            
            # Check if cancelled during wait
            if self.cancel_requested:
                self._log("🛑 Download stopped")
                self._on_complete(False, {'reason': 'cancelled'})
                return
            
            # Handle completion
            if return_code == 0:
                self._log("✅ Download completed successfully!")
                self._on_complete(True, {
                    'files': downloaded_files,
                    'output_path': options.output_path,
                    'options': options.to_dict()
                })
            else:
                self._log(f"❌ Download failed with return code: {return_code}")
                self._on_complete(False, {
                    'reason': 'failed',
                    'return_code': return_code
                })
        
        except FileNotFoundError:
            error_msg = "yt-dlp not found! Please install yt-dlp first."
            self._log(f"❌ {error_msg}")
            self._on_error(error_msg)
            self._on_complete(False, {'reason': 'missing_dependency'})
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._log(f"❌ {error_msg}")
            self._on_error(error_msg)
            self._on_complete(False, {'reason': 'error', 'error': str(e)})
        
        finally:
            self.is_downloading = False
            self.current_process = None
    
    def cancel_download(self) -> bool:
        """Cancel current download"""
        if not self.is_downloading:
            return False
        
        self.cancel_requested = True
        self._log("🛑 Cancel requested - stopping after current file...")
        
        if self.current_process:
            try:
                self.current_process.terminate()
                # Give it a moment to terminate gracefully
                try:
                    self.current_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.current_process.kill()
                    self._log("🔨 Process force-killed")
            except Exception as e:
                self._log(f"⚠️ Error during cancellation: {e}")
        
        return True
    
    def is_busy(self) -> bool:
        """Check if download is in progress"""
        return self.is_downloading

class UpdateChecker:
    """Checks for yt-dlp updates"""
    
    def __init__(self):
        self.callbacks: Dict[str, Callable] = {}
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set callback functions"""
        self.callbacks = callbacks
    
    def _log(self, message: str):
        """Send log message"""
        if 'on_log' in self.callbacks:
            self.callbacks['on_log'](message)
    
    def check_version(self) -> Optional[str]:
        """Get current yt-dlp version"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=config.TIMEOUTS['update_check']
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self._log(f"yt-dlp version: {version}")
                return version
            return None
        except Exception as e:
            self._log(f"Could not check yt-dlp version: {e}")
            return None
    
    def update_ytdlp(self) -> bool:
        """Update yt-dlp to latest version"""
        try:
            self._log("🔄 Checking for yt-dlp updates...")
            
            result = subprocess.run(
                ['yt-dlp', '-U'],
                capture_output=True,
                text=True,
                timeout=config.TIMEOUTS['update_install']
            )
            
            if result.returncode == 0:
                if "Updated" in result.stdout:
                    self._log("✅ yt-dlp updated to latest version")
                    return True
                elif "up to date" in result.stdout:
                    self._log("✅ yt-dlp is already up to date")
                    return True
                else:
                    self._log("ℹ️ yt-dlp update completed")
                    return True
            else:
                self._log(f"❌ Update failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            self._log("❌ Update timed out")
            return False
        except Exception as e:
            self._log(f"❌ Error updating yt-dlp: {e}")
            return False

class YouTubeDownloaderCore:
    """Main core class that coordinates all functionality"""
    
    def __init__(self):
        self.download_engine = DownloadEngine()
        self.update_checker = UpdateChecker()
        self.callbacks: Dict[str, Callable] = {}
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set callback functions for UI communication"""
        self.callbacks = callbacks
        self.download_engine.set_callbacks(callbacks)
        self.update_checker.set_callbacks(callbacks)
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information"""
        return self.download_engine.get_video_info(url)
    
    def get_playlist_info(self, url: str) -> Optional[PlaylistInfo]:
        """Get playlist information"""
        return self.download_engine.get_playlist_info(url)
    
    def start_download(self, url: str, options: DownloadOptions) -> bool:
        """Start download"""
        return self.download_engine.download(url, options)
    
    def cancel_download(self) -> bool:
        """Cancel current download"""
        return self.download_engine.cancel_download()
    
    def is_downloading(self) -> bool:
        """Check if download is in progress"""
        return self.download_engine.is_busy()
    
    def check_ytdlp_version(self) -> Optional[str]:
        """Get yt-dlp version"""
        return self.update_checker.check_version()
    
    def update_ytdlp(self) -> bool:
        """Update yt-dlp"""
        return self.update_checker.update_ytdlp()
    
    def validate_url(self, url: str) -> bool:
        """Validate YouTube URL"""
        return URLValidator.is_valid_youtube_url(url)
    
    def is_playlist_url(self, url: str) -> bool:
        """Check if URL is playlist"""
        return URLValidator.is_playlist_url(url)
