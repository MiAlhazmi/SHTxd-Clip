"""
User Interface for SHTxd Clip
Contains all GUI components and layouts using CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import config
from utils import SettingsManager, HistoryManager, ThemeManager, FileManager, Logger, truncate_text
from core import YouTubeDownloaderCore, DownloadOptions, VideoInfo, PlaylistInfo

class VideoPreviewWidget:
    """Widget for displaying video preview information"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=["#f8f9fa", "#2b2b2b"])
        
    def show_loading(self):
        """Show loading state"""
        self.clear()
        self.frame.pack(fill="x", padx=15, pady=(0, 15))
        
        loading_label = ctk.CTkLabel(
            self.frame,
            text="🔄 Loading video information...",
            font=ctk.CTkFont(**config.FONTS['text'])
        )
        loading_label.pack(pady=20)
    
    def show_video_info(self, video_info: VideoInfo):
        """Display video information"""
        self.clear()
        self.frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Container
        info_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        info_container.pack(fill="x", padx=20, pady=15)
        
        # Content frame
        content_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        content_frame.pack(fill="x")
        
        # Thumbnail placeholder
        thumbnail_frame = ctk.CTkFrame(
            content_frame, 
            corner_radius=15, 
            width=120, 
            height=90,
            fg_color=["#f0f0f0", "#3a3a3a"]
        )
        thumbnail_frame.pack(side="left", padx=(0, 15))
        thumbnail_frame.pack_propagate(False)
        
        thumbnail_icon = ctk.CTkLabel(
            thumbnail_frame,
            text="🎬",
            font=ctk.CTkFont(size=32)
        )
        thumbnail_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Video info
        info_text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_text_frame.pack(side="left", fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            info_text_frame,
            text=video_info.title,
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400,
            anchor="w",
            justify="left",
            text_color=config.UI_COLORS['primary']
        )
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Channel and duration
        details_frame = ctk.CTkFrame(info_text_frame, fg_color="transparent")
        details_frame.pack(fill="x", pady=(0, 5))
        
        channel_label = ctk.CTkLabel(
            details_frame,
            text=f"📺 {video_info.uploader}",
            font=ctk.CTkFont(**config.FONTS['text']),
            text_color="gray60",
            anchor="w"
        )
        channel_label.pack(anchor="w")
        
        duration_label = ctk.CTkLabel(
            details_frame,
            text=f"⏱️ Duration: {video_info.get_formatted_duration()}",
            font=ctk.CTkFont(**config.FONTS['text']),
            text_color="gray60",
            anchor="w"
        )
        duration_label.pack(anchor="w")
        
        # Stats
        stats_frame = ctk.CTkFrame(info_text_frame, fg_color="transparent")
        stats_frame.pack(fill="x")
        
        if video_info.view_count:
            views_label = ctk.CTkLabel(
                stats_frame,
                text=f"👁️ {video_info.get_formatted_view_count()} views",
                font=ctk.CTkFont(**config.FONTS['small']),
                text_color="gray60",
                anchor="w"
            )
            views_label.pack(anchor="w")
        
        upload_date = video_info.get_formatted_upload_date()
        if upload_date != "Unknown":
            date_label = ctk.CTkLabel(
                stats_frame,
                text=f"📅 Uploaded: {upload_date}",
                font=ctk.CTkFont(**config.FONTS['small']),
                text_color="gray60",
                anchor="w"
            )
            date_label.pack(anchor="w")
    
    def show_error(self, error_msg: str):
        """Show error message"""
        self.clear()
        self.frame.pack(fill="x", padx=15, pady=(0, 15))
        
        error_label = ctk.CTkLabel(
            self.frame,
            text=f"❌ {error_msg}",
            font=ctk.CTkFont(**config.FONTS['text']),
            text_color="red"
        )
        error_label.pack(pady=20)
    
    def clear(self):
        """Clear the widget"""
        for widget in self.frame.winfo_children():
            widget.destroy()
    
    def hide(self):
        """Hide the widget"""
        self.frame.pack_forget()

class PlaylistOptionsWidget:
    """Widget for playlist-specific options"""
    
    def __init__(self, parent):
        self.parent = parent

        # Initialize variables first
        self.quantity_var = tk.StringVar(value=config.DEFAULT_PLAYLIST_QUANTITY)
        self.start_var = tk.StringVar(value="1")
        self.end_var = tk.StringVar(value="10")

        # Create frame and setup UI
        self.frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=["#e8f5e8", "#1a3d1a"])
        self.setup_ui()
        self.frame.pack_forget()  # Initially hidden

    def setup_ui(self):
        """Setup the playlist options UI"""
        # Header
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))

        icon = ctk.CTkLabel(header, text="📚", font=ctk.CTkFont(size=16))
        icon.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            header,
            text="Playlist Information",
            font=ctk.CTkFont(**config.FONTS['label'])
        )
        title.pack(side="left")

        # Info label
        self.info_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(**config.FONTS['small']),
            text_color="gray70",
            anchor="w",
            justify="left"
        )
        self.info_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Quantity controls
        controls_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Quantity selector
        quantity_label = ctk.CTkLabel(
            controls_frame,
            text="🎯 Download:",
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold")
        )
        quantity_label.pack(side="left", padx=(0, 10))

        self.quantity_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=config.PLAYLIST_QUANTITY_OPTIONS,
            variable=self.quantity_var,
            width=100,
            height=32,
            corner_radius=10,
            font=ctk.CTkFont(**config.FONTS['small'])
        )
        self.quantity_menu.pack(side="left", padx=(0, 15))

        # Custom range
        range_label = ctk.CTkLabel(
            controls_frame,
            text="📊 Custom Range:",
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold")
        )
        range_label.pack(side="left", padx=(0, 8))

        self.start_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.start_var,
            width=50,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(**config.FONTS['small'])
        )
        self.start_entry.pack(side="left", padx=(0, 5))

        dash_label = ctk.CTkLabel(
            controls_frame,
            text="→",
            font=ctk.CTkFont(size=14)
        )
        dash_label.pack(side="left", padx=3)

        self.end_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.end_var,
            width=50,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(**config.FONTS['small'])
        )
        self.end_entry.pack(side="left", padx=(5, 0))

    def show_playlist_info(self, playlist_info: PlaylistInfo):
        """Display playlist information"""
        # Format info text
        summary = f"📚 Found {playlist_info.total_count} videos ({playlist_info.get_formatted_duration()})"

        # Get preview titles
        preview_titles = playlist_info.get_preview_titles(3)
        formatted_titles = [f"  • {truncate_text(title, 60)}" for title in preview_titles]

        preview_text = "\n".join(formatted_titles)
        if playlist_info.total_count > 3:
            preview_text += f"\n  ... and {playlist_info.total_count - 3} more videos"

        info_text = f"{summary}\n\nPreview:\n{preview_text}"
        self.info_label.configure(text=info_text)

        # Update quantity options
        options = ["5", "10", "20"]
        if playlist_info.total_count > 20:
            options.append("50")
        if playlist_info.total_count > 50:
            options.append("100")
        options.append("All")

        self.quantity_menu.configure(values=options)
        self.end_var.set(str(min(10, playlist_info.total_count)))

    def show_error(self, error_msg: str):
        """Show error message"""
        self.info_label.configure(text=f"❌ {error_msg}")

    def show(self):
        """Show the widget"""
        self.frame.pack(fill="x", pady=(10, 0))

    def hide(self):
        """Hide the widget"""
        self.frame.pack_forget()

    def get_options(self) -> Dict[str, Any]:
        """Get current playlist options"""
        return {
            'quantity': self.quantity_var.get(),
            'start': self.start_var.get(),
            'end': self.end_var.get()
        }

class DownloadTab:
    """Main download tab interface"""

    def __init__(self, parent, core: YouTubeDownloaderCore):
        self.parent = parent
        self.core = core

        # Variables
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value=config.DEFAULT_QUALITY)
        self.playlist_var = tk.BooleanVar()
        self.subtitles_var = tk.BooleanVar()
        self.thumbnail_var = tk.BooleanVar()
        self.download_path = tk.StringVar(value=str(config.DEFAULT_DOWNLOAD_PATH))

        # State
        self.current_video_info: Optional[VideoInfo] = None
        self.current_playlist_info: Optional[PlaylistInfo] = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the download tab UI"""
        # Main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent,
            corner_radius=0,
            fg_color="transparent"
        )
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Title
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(0, 25))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🎬 SHTxd Clip",
            font=ctk.CTkFont(**config.FONTS['title']),
            text_color=config.UI_COLORS['primary']
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Download videos and playlists with ease",
            font=ctk.CTkFont(**config.FONTS['text']),
            text_color="gray60"
        )
        subtitle_label.pack(pady=(5, 0))

        # URL Input Section
        self.setup_url_section()

        # Quality Selection
        self.setup_quality_section()

        # Advanced Options
        self.setup_advanced_options()

        # Download Path
        self.setup_path_section()

        # Progress Section
        self.setup_progress_section()

        # Download Button
        self.setup_download_button()

        # Log Section
        self.setup_log_section()

    def setup_url_section(self):
        """Setup URL input section"""
        url_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        url_frame.pack(fill="x", pady=(0, 20))

        # Header
        header = ctk.CTkFrame(url_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 5))

        icon = ctk.CTkLabel(header, text="🔗", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Video URL",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        # Input
        input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.url_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.url_var,
            font=ctk.CTkFont(**config.FONTS['text']),
            height=45,
            corner_radius=15,
            border_width=2,
            placeholder_text="🎥 Paste your YouTube video or playlist URL here..."
        )
        self.url_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.url_entry.bind('<Return>', lambda e: self.preview_video())

        self.preview_btn = ctk.CTkButton(
            input_frame,
            text="🔍 Preview",
            command=self.preview_video,
            width=100,
            height=45,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            fg_color=config.UI_COLORS['primary'],
            hover_color=["#1976D2", "#1565C0"]
        )
        self.preview_btn.pack(side="right")

        # Preview widget
        self.video_preview = VideoPreviewWidget(url_frame)

    def setup_quality_section(self):
        """Setup quality selection section"""
        quality_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        quality_frame.pack(fill="x", pady=(0, 20))

        # Header
        header = ctk.CTkFrame(quality_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 15))

        icon = ctk.CTkLabel(header, text="⚙️", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Download Quality",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        # Quality options
        options_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(0, 20))

        for option in config.QUALITY_OPTIONS:
            self.create_quality_option(options_frame, option)

    def create_quality_option(self, parent, option: Dict[str, Any]):
        """Create a quality option widget"""
        option_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            border_width=1,
            border_color=config.UI_COLORS['border']
        )
        option_frame.pack(fill="x", pady=5)

        inner_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=15, pady=12)

        # Radio button
        radio = ctk.CTkRadioButton(
            inner_frame,
            text="",
            variable=self.quality_var,
            value=option['value'],
            font=ctk.CTkFont(**config.FONTS['text']),
            radiobutton_width=20,
            radiobutton_height=20
        )
        radio.pack(side="left", padx=(0, 15))

        # Icon
        icon = ctk.CTkLabel(
            inner_frame,
            text=option['icon'],
            font=ctk.CTkFont(size=18)
        )
        icon.pack(side="left", padx=(0, 12))

        # Text
        text_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        title = ctk.CTkLabel(
            text_frame,
            text=option['name'],
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            anchor="w",
            text_color=option['colors'][0]
        )
        title.pack(anchor="w", pady=(0, 2))

        desc = ctk.CTkLabel(
            text_frame,
            text=option['description'],
            font=ctk.CTkFont(**config.FONTS['small']),
            text_color="gray60",
            anchor="w"
        )
        desc.pack(anchor="w")

    def setup_advanced_options(self):
        """Setup advanced options section"""
        advanced_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        advanced_frame.pack(fill="x", pady=(0, 20))

        # Header
        header = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="🛠️", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Advanced Options",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        # Options
        options_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Create checkboxes
        for i, option in enumerate(config.ADVANCED_OPTIONS):
            var = getattr(self, f"{option['key']}_var")
            command = self.on_playlist_toggle if option['key'] == 'playlist' else None

            self.create_advanced_option(options_frame, option, var, command)

        # Playlist options widget
        self.playlist_options = PlaylistOptionsWidget(options_frame)

    def create_advanced_option(self, parent, option: Dict[str, Any],
                              variable: tk.BooleanVar, command: Optional[Callable]):
        """Create an advanced option widget"""
        option_frame = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color=["#f8f9fa", "#2b2b2b"]
        )
        option_frame.pack(fill="x", pady=3)

        inner_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=15, pady=10)

        checkbox = ctk.CTkCheckBox(
            inner_frame,
            text=option['text'],
            variable=variable,
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            command=command
        )
        checkbox.pack(anchor="w")

        desc = ctk.CTkLabel(
            inner_frame,
            text=option['description'],
            font=ctk.CTkFont(**config.FONTS['tiny']),
            text_color="gray60",
            anchor="w"
        )
        desc.pack(anchor="w", padx=(25, 0))

    def setup_path_section(self):
        """Setup download path section"""
        path_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        path_frame.pack(fill="x", pady=(0, 20))

        # Header
        header = ctk.CTkFrame(path_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="📁", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Download Location",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        # Path input
        input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.path_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.download_path,
            font=ctk.CTkFont(**config.FONTS['text']),
            height=45,
            corner_radius=15,
            border_width=2
        )
        self.path_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            input_frame,
            text="📂 Browse",
            command=self.browse_folder,
            width=120,
            height=45,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            fg_color=config.UI_COLORS['secondary'],
            hover_color=["#455A64", "#37474F"]
        )
        browse_btn.pack(side="right")

    def setup_progress_section(self):
        """Setup progress section"""
        progress_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        progress_frame.pack(fill="x", pady=(0, 20))

        # Header
        header = ctk.CTkFrame(progress_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="📊", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            header,
            text="Download Progress",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        title.pack(side="left")

        # Progress info
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(**config.FONTS['label']),
            text_color=config.UI_COLORS['success']
        )
        self.progress_label.pack(pady=(0, 8))

        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            corner_radius=10,
            height=20,
            border_width=1,
            border_color=config.UI_COLORS['border']
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)

        self.speed_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(**config.FONTS['small']),
            text_color="gray60"
        )
        self.speed_label.pack(pady=(0, 20))

    def setup_download_button(self):
        """Setup download button"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))

        self.download_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Download Video",
            command=self.toggle_download,
            font=ctk.CTkFont(**config.FONTS['button']),
            height=55,
            corner_radius=25,
            border_width=2,
            border_color=["#1976D2", "#0D47A1"],
            fg_color=config.UI_COLORS['primary'],
            hover_color=["#1976D2", "#1565C0"],
            text_color="white"
        )
        self.download_btn.pack(fill="x")

    def setup_log_section(self):
        """Setup log section"""
        log_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        log_frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(log_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="📋", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Download Log",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        clear_btn = ctk.CTkButton(
            header,
            text="🗑️ Clear",
            command=self.clear_log,
            width=80,
            height=30,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['small']),
            fg_color=config.UI_COLORS['danger'],
            hover_color=["#D84315", "#BF360C"]
        )
        clear_btn.pack(side="right")

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(**config.FONTS['log']),
            wrap="word",
            height=150,
            corner_radius=15,
            border_width=1,
            border_color=config.UI_COLORS['border']
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Event handlers
    def preview_video(self):
        """Preview video or playlist"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", config.ERROR_MESSAGES['missing_url'])
            return

        if not self.core.validate_url(url):
            messagebox.showerror("Invalid URL", config.ERROR_MESSAGES['invalid_url'])
            return

        # Check for playlist
        if self.core.is_playlist_url(url) and not self.playlist_var.get():
            if messagebox.askyesno("Playlist Detected",
                                 "This appears to be a playlist URL. Would you like to enable playlist mode?"):
                self.playlist_var.set(True)
                self.on_playlist_toggle()
                return

        self.video_preview.show_loading()

        if self.playlist_var.get() and self.core.is_playlist_url(url):
            threading.Thread(target=self._get_playlist_info, args=(url,), daemon=True).start()
        else:
            threading.Thread(target=self._get_video_info, args=(url,), daemon=True).start()

    def _get_video_info(self, url: str):
        """Get video info in background thread"""
        video_info = self.core.get_video_info(url)
        if video_info:
            self.current_video_info = video_info
            self.main_frame.after(0, lambda: self.video_preview.show_video_info(video_info))
        else:
            self.main_frame.after(0, lambda: self.video_preview.show_error("Could not fetch video information"))

    def _get_playlist_info(self, url: str):
        """Get playlist info in background thread"""
        playlist_info = self.core.get_playlist_info(url)
        if playlist_info:
            self.current_playlist_info = playlist_info
            self.main_frame.after(0, lambda: self.playlist_options.show_playlist_info(playlist_info))
        else:
            self.main_frame.after(0, lambda: self.playlist_options.show_error("Could not fetch playlist information"))

    def on_playlist_toggle(self):
        """Handle playlist checkbox toggle"""
        if self.playlist_var.get():
            self.playlist_options.show()
            # If we have a URL, try to get playlist info
            url = self.url_var.get().strip()
            if url and self.core.is_playlist_url(url):
                threading.Thread(target=self._get_playlist_info, args=(url,), daemon=True).start()
        else:
            self.playlist_options.hide()

    def browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)

    def toggle_download(self):
        """Toggle between download and cancel"""
        if self.core.is_downloading():
            self.cancel_download()
        else:
            self.start_download()

    def start_download(self):
        """Start download process"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", config.ERROR_MESSAGES['missing_url'])
            return

        if not self.core.validate_url(url):
            messagebox.showerror("Invalid URL", config.ERROR_MESSAGES['invalid_url'])
            return

        # Create download options
        options = DownloadOptions()
        options.quality = self.quality_var.get()
        options.output_path = self.download_path.get()
        options.download_playlist = self.playlist_var.get()
        options.download_subtitles = self.subtitles_var.get()
        options.download_thumbnail = self.thumbnail_var.get()

        if self.playlist_var.get():
            playlist_opts = self.playlist_options.get_options()
            options.playlist_quantity = playlist_opts['quantity']
            try:
                options.playlist_start = int(playlist_opts['start']) if playlist_opts['start'].isdigit() else 1
                options.playlist_end = int(playlist_opts['end']) if playlist_opts['end'].isdigit() else 10
            except:
                options.playlist_start = 1
                options.playlist_end = 10

        # Update UI for download state
        self.download_btn.configure(
            text="⏹️ Cancel Download",
            fg_color=config.UI_COLORS['cancel']
        )
        self.progress_bar.set(0)
        self.progress_label.configure(text="Initializing download...")
        self.speed_label.configure(text="")

        # Start download
        success = self.core.start_download(url, options)
        if not success:
            self.reset_download_state()

    def cancel_download(self):
        """Cancel current download"""
        if messagebox.askyesno("Cancel Download", "Cancel the current download?"):
            self.core.cancel_download()
            self.download_btn.configure(text="⏹️ Stopping...", state="disabled")

    def reset_download_state(self):
        """Reset download UI state"""
        self.download_btn.configure(
            text="🚀 Download Video",
            state="normal",
            fg_color=config.UI_COLORS['primary']
        )
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to download")
        self.speed_label.configure(text="")

    def clear_log(self):
        """Clear log"""
        self.log_text.delete("1.0", "end")
        self.add_log_message(config.LOG_MESSAGES['log_cleared'])

    # Callback methods for core
    def add_log_message(self, message: str):
        """Add message to log"""
        formatted_message = Logger.format_message(message) + "\n"
        self.log_text.insert("end", formatted_message)
        self.log_text.see("end")
        self.main_frame.update_idletasks()

    def update_progress(self, progress_data: Dict[str, Any]):
        """Update progress display"""
        if 'percentage' in progress_data:
            self.progress_bar.set(progress_data['percentage'] / 100)
            self.progress_label.configure(text=f"Downloading... {progress_data['percentage']:.1f}%")

        if 'speed' in progress_data and 'eta' in progress_data:
            self.speed_label.configure(text=f"Speed: {progress_data['speed']} • ETA: {progress_data['eta']}")

        if 'status_text' in progress_data:
            self.progress_label.configure(text=progress_data['status_text'])

    def download_finished(self, success: bool, data: Dict[str, Any]):
        """Handle download completion"""
        self.reset_download_state()

        if success:
            self.progress_label.configure(text="Download completed!")
            self.progress_bar.set(1.0)

            # Show completion dialog
            files = data.get('files', [])
            output_path = data.get('output_path', '')

            if files:
                file_name = Path(files[0]).name
                message = f"✅ Download completed!\n\nFile: {file_name}\nLocation: {output_path}"
            else:
                message = f"✅ Download completed!\nLocation: {output_path}"

            def show_completion():
                messagebox.showinfo("Download Complete", message)
                if messagebox.askyesno("Open Folder", "Would you like to open the download folder?"):
                    FileManager.open_folder(output_path)

            self.main_frame.after(0, show_completion)
        else:
            reason = data.get('reason', 'unknown')
            if reason == 'cancelled':
                self.progress_label.configure(text="Download cancelled")
            else:
                self.progress_label.configure(text="Download failed")

    def show_error(self, error: str):
        """Show error message"""
        messagebox.showerror("Error", error)

    def get_settings(self) -> Dict[str, Any]:
        """Get current tab settings"""
        return {
            'download_path': self.download_path.get(),
            'default_quality': self.quality_var.get()
        }

    def load_settings(self, settings: Dict[str, Any]):
        """Load settings into tab"""
        self.download_path.set(settings.get('download_path', str(config.DEFAULT_DOWNLOAD_PATH)))
        self.quality_var.set(settings.get('default_quality', config.DEFAULT_QUALITY))

class HistoryTab:
    """Download history tab interface"""

    def __init__(self, parent):
        self.parent = parent
        self.history_manager = HistoryManager()
        self.setup_ui()
        self.refresh_history()

    def setup_ui(self):
        """Setup history tab UI"""
        main_frame = ctk.CTkScrollableFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        header_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        header_frame.pack(fill="x", pady=(0, 20))

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=20)

        icon = ctk.CTkLabel(header_content, text="📚", font=ctk.CTkFont(size=24))
        icon.pack(side="left", padx=(0, 10))

        title = ctk.CTkLabel(
            header_content,
            text="Download History",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=config.UI_COLORS['primary']
        )
        title.pack(side="left")

        clear_btn = ctk.CTkButton(
            header_content,
            text="🗑️ Clear All",
            command=self.clear_history,
            width=120,
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            fg_color=config.UI_COLORS['danger'],
            hover_color=["#D84315", "#BF360C"]
        )
        clear_btn.pack(side="right")

        # History list
        self.history_scrollable = ctk.CTkScrollableFrame(main_frame, height=500, corner_radius=20)
        self.history_scrollable.pack(fill="both", expand=True)

    def refresh_history(self):
        """Refresh history display"""
        # Clear existing widgets
        for widget in self.history_scrollable.winfo_children():
            widget.destroy()

        history = self.history_manager.load_history()

        if not history:
            no_history = ctk.CTkLabel(
                self.history_scrollable,
                text="No download history yet",
                font=ctk.CTkFont(**config.FONTS['text']),
                text_color="gray70"
            )
            no_history.pack(pady=50)
            return

        # Show last 20 entries
        for item in reversed(history[-20:]):
            self.create_history_item(item)

    def create_history_item(self, item: Dict[str, Any]):
        """Create history item widget"""
        item_frame = ctk.CTkFrame(self.history_scrollable, corner_radius=10)
        item_frame.pack(fill="x", pady=5)

        # Title
        title = ctk.CTkLabel(
            item_frame,
            text=truncate_text(item.get('title', 'Unknown Title'), 80),
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", padx=15, pady=(10, 2))

        # Details
        date = item.get('date', 'Unknown')
        quality = item.get('quality', 'Unknown')
        path = Path(item.get('path', '')).name

        details = f"📅 {date} • 🎯 {quality} • 📁 {path}"
        details_label = ctk.CTkLabel(
            item_frame,
            text=details,
            font=ctk.CTkFont(**config.FONTS['tiny']),
            text_color="gray70",
            anchor="w"
        )
        details_label.pack(anchor="w", padx=15, pady=(0, 10))

    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all download history?"):
            self.history_manager.clear_history()
            self.refresh_history()

    def add_entry(self, title: str, url: str, quality: str, file_path: str):
        """Add new history entry"""
        history = self.history_manager.load_history()
        history = self.history_manager.add_entry(history, title, url, quality, file_path)
        self.history_manager.save_history(history)
        self.refresh_history()

class SettingsTab:
    """Settings tab interface"""

    def __init__(self, parent, core: YouTubeDownloaderCore):
        self.parent = parent
        self.core = core
        self.settings_manager = SettingsManager()
        self.theme_var = tk.StringVar(value=config.DEFAULT_THEME)
        self.quality_var = tk.StringVar(value=config.DEFAULT_QUALITY)
        self.setup_ui()

    def setup_ui(self):
        """Setup settings tab UI"""
        main_frame = ctk.CTkScrollableFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Title
        title_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        title_frame.pack(fill="x", pady=(0, 25))

        title_content = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_content.pack(fill="x", padx=20, pady=20)

        icon = ctk.CTkLabel(title_content, text="⚙️", font=ctk.CTkFont(size=24))
        icon.pack(side="left", padx=(0, 10))

        title = ctk.CTkLabel(
            title_content,
            text="Settings & Preferences",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=config.UI_COLORS['primary']
        )
        title.pack(side="left")

        # Theme settings
        self.setup_theme_section(main_frame)

        # Quality settings
        self.setup_quality_section(main_frame)

        # Update section
        self.setup_update_section(main_frame)

        # Save button
        save_btn = ctk.CTkButton(
            main_frame,
            text="💾 Save All Settings",
            command=self.save_settings,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(**config.FONTS['button']),
            fg_color=config.UI_COLORS['primary'],
            hover_color=["#1976D2", "#1565C0"]
        )
        save_btn.pack(fill="x", pady=25)

    def setup_theme_section(self, parent):
        """Setup theme section"""
        theme_frame = ctk.CTkFrame(
            parent,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        theme_frame.pack(fill="x", pady=(0, 20))

        header = ctk.CTkFrame(theme_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="🎨", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Appearance",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        self.theme_option = ctk.CTkOptionMenu(
            theme_frame,
            values=ThemeManager.get_available_themes(),
            variable=self.theme_var,
            command=self.change_theme,
            width=200,
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'])
        )
        self.theme_option.pack(anchor="w", padx=20, pady=(0, 20))

    def setup_quality_section(self, parent):
        """Setup default quality section"""
        quality_frame = ctk.CTkFrame(
            parent,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        quality_frame.pack(fill="x", pady=(0, 20))

        header = ctk.CTkFrame(quality_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="🎯", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Default Download Quality",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        quality_values = [opt['value'] for opt in config.QUALITY_OPTIONS]
        self.quality_option = ctk.CTkOptionMenu(
            quality_frame,
            values=quality_values,
            variable=self.quality_var,
            width=200,
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'])
        )
        self.quality_option.pack(anchor="w", padx=20, pady=(0, 20))

    def setup_update_section(self, parent):
        """Setup update section"""
        update_frame = ctk.CTkFrame(
            parent,
            corner_radius=20,
            border_width=2,
            border_color=config.UI_COLORS['border']
        )
        update_frame.pack(fill="x", pady=(0, 20))

        header = ctk.CTkFrame(update_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        icon = ctk.CTkLabel(header, text="🔄", font=ctk.CTkFont(size=20))
        icon.pack(side="left", padx=(0, 8))

        label = ctk.CTkLabel(
            header,
            text="Updates & Maintenance",
            font=ctk.CTkFont(**config.FONTS['section_header'])
        )
        label.pack(side="left")

        # yt-dlp update button (existing)
        update_btn = ctk.CTkButton(
            update_frame,
            text="🔄 Update yt-dlp",
            command=self.update_ytdlp,
            width=200,
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            fg_color=config.UI_COLORS['success'],
            hover_color=["#388E3C", "#2E7D32"]
        )
        update_btn.pack(anchor="w", padx=20, pady=(0, 10))

        # NEW: App update button
        app_update_btn = ctk.CTkButton(
            update_frame,
            text="🔄 Check for App Updates",
            command=self.check_app_updates,  # Now this will work!
            width=200,
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(**config.FONTS['text'], weight="bold"),
            fg_color=config.UI_COLORS['primary'],
            hover_color=["#1976D2", "#1565C0"]
        )
        app_update_btn.pack(anchor="w", padx=20, pady=(0, 20))

    def check_app_updates(self):
        """Check for app updates"""

        def update_worker():
            update_info = self.core.check_app_updates()
            def show_result():
                if update_info.get('update_available'):
                    self.show_update_dialog(update_info)
                elif update_info.get('error'):
                    messagebox.showerror("Update Check Failed",
                                         f"Could not check for updates:\n{update_info['error']}")
                else:
                    messagebox.showinfo("Updates", "You're running the latest version!")

            self.parent.after(0, show_result)

        threading.Thread(target=update_worker, daemon=True).start()

    def show_update_dialog(self, update_info):
        """Show update available dialog"""
        version = update_info['latest_version']
        release_name = update_info.get('release_name', f'Version {version}')

        message = f"🎉 {release_name} is available!\n\n"
        message += f"Current version: {config.APP_VERSION}\n"
        message += f"Latest version: {version}\n\n"
        message += "Would you like to download it from GitHub?"

        if messagebox.askyesno("Update Available", message):
            # Open GitHub releases page in browser
            import webbrowser
            webbrowser.open(f"https://github.com/{config.GITHUB_REPO}/releases/latest")

    def change_theme(self, theme: str):
        """Change application theme"""
        ThemeManager.apply_theme(theme)

    def update_ytdlp(self):
        """Update yt-dlp"""
        def update_worker():
            success = self.core.update_ytdlp()
            if success:
                self.parent.after(0, lambda: messagebox.showinfo("Update", "yt-dlp updated successfully!"))
            else:
                self.parent.after(0, lambda: messagebox.showerror("Update", "Failed to update yt-dlp"))

        threading.Thread(target=update_worker, daemon=True).start()

    def save_settings(self):
        """Save all settings"""
        settings = {
            'theme': self.theme_var.get(),
            'default_quality': self.quality_var.get()
        }

        if self.settings_manager.save_settings(settings):
            messagebox.showinfo("Settings", "Settings saved successfully!")
        else:
            messagebox.showerror("Settings", "Failed to save settings")

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return {
            'theme': self.theme_var.get(),
            'default_quality': self.quality_var.get()
        }

    def load_settings(self, settings: Dict[str, Any]):
        """Load settings"""
        self.theme_var.set(settings.get('theme', config.DEFAULT_THEME))
        self.quality_var.set(settings.get('default_quality', config.DEFAULT_QUALITY))

class YouTubeDownloaderUI:
    """Main UI class that coordinates all tabs and core interaction"""

    def __init__(self):
        # Initialize core
        self.core = YouTubeDownloaderCore()
        self.settings_manager = SettingsManager()
        self.history_manager = HistoryManager()

        # Setup core callbacks
        self.setup_core_callbacks()

        # Create main window
        self.setup_main_window()

        # Create tabs
        self.setup_tabs()

        # Load settings
        self.load_settings()

        # Initialize core with update check
        self.initialize_core()

    def setup_main_window(self):
        """Setup main application window"""
        # Configure CustomTkinter
        ctk.set_appearance_mode(config.CTK_CONFIG['appearance_mode'])
        ctk.set_default_color_theme(config.CTK_CONFIG['color_theme'])

        # Create window
        self.root = ctk.CTk()
        self.root.title(config.APP_NAME)
        self.root.geometry(config.DEFAULT_WINDOW_SIZE)
        self.root.minsize(*config.MIN_WINDOW_SIZE)
        self.root.resizable(True, True)

    def setup_tabs(self):
        """Setup tabbed interface"""
        # Create notebook
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        download_tab = self.notebook.add("Download")
        history_tab = self.notebook.add("History")
        settings_tab = self.notebook.add("Settings")

        # Initialize tab classes
        self.download_tab = DownloadTab(download_tab, self.core)
        self.history_tab = HistoryTab(history_tab)
        self.settings_tab = SettingsTab(settings_tab, self.core)

    def setup_core_callbacks(self):
        """Setup callbacks for core communication"""
        callbacks = {
            'on_log': self.on_log,
            'on_progress': self.on_progress,
            'on_complete': self.on_complete,
            'on_error': self.on_error
        }
        self.core.set_callbacks(callbacks)

    def initialize_core(self):
        """Initialize core with startup tasks"""
        def startup_worker():
            # Check yt-dlp version
            self.core.check_ytdlp_version()

            # Log startup message
            self.on_log(config.LOG_MESSAGES['app_ready'])
            self.on_log(config.LOG_MESSAGES['ui_loaded'])

        threading.Thread(target=startup_worker, daemon=True).start()

    def load_settings(self):
        """Load application settings"""
        settings = self.settings_manager.load_settings()

        # Apply theme
        ThemeManager.apply_theme(settings.get('theme', config.DEFAULT_THEME))

        # Load tab settings
        self.download_tab.load_settings(settings)
        self.settings_tab.load_settings(settings)

    def save_settings(self):
        """Save application settings"""
        # Collect settings from all tabs
        settings = {}
        settings.update(self.download_tab.get_settings())
        settings.update(self.settings_tab.get_settings())

        # Add window geometry
        settings['window_geometry'] = self.root.geometry()

        self.settings_manager.save_settings(settings)

    # Core callback implementations
    def on_log(self, message: str):
        """Handle log messages from core"""
        self.download_tab.add_log_message(message)

    def on_progress(self, progress_data: Dict[str, Any]):
        """Handle progress updates from core"""
        self.download_tab.update_progress(progress_data)

    def on_complete(self, success: bool, data: Dict[str, Any]):
        """Handle download completion from core"""
        self.download_tab.download_finished(success, data)

        # Add to history if successful
        if success and self.download_tab.current_video_info:
            self.history_tab.add_entry(
                self.download_tab.current_video_info.title,
                self.download_tab.url_var.get(),
                self.download_tab.quality_var.get(),
                data.get('output_path', '')
            )

    def on_error(self, error: str):
        """Handle errors from core"""
        self.download_tab.show_error(error)

    def on_closing(self):
        """Handle application closing"""
        self.save_settings()
        self.root.quit()

    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()