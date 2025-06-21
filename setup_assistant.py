"""
First-time setup assistant for SHTxd Clip
Helps users install Python, pip, and yt-dlp
"""

import os
import sys
import shutil
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from pathlib import Path
from typing import Dict, Any, Optional
import config

class SetupAssistant:
    """Handles first-time setup detection and guidance"""
    
    def __init__(self):
        self.setup_file = Path.home() / ".shtxd_clip_setup_complete"
        self.callbacks = {}
    
    def set_callbacks(self, callbacks: Dict[str, Any]):
        """Set callback functions"""
        self.callbacks = callbacks
    
    def _log(self, message: str):
        """Send log message"""
        if 'on_log' in self.callbacks:
            self.callbacks['on_log'](message)
        print(message)
    
    def is_setup_complete(self) -> bool:
        """Check if user has completed setup before"""
        return self.setup_file.exists()
    
    def mark_setup_complete(self):
        """Mark setup as completed"""
        try:
            self.setup_file.touch()
            self._log("✅ Setup marked as complete")
        except Exception as e:
            self._log(f"⚠️ Could not mark setup complete: {e}")
    
    def check_python_installation(self) -> Dict[str, Any]:
        """Check Python installation status"""
        result = {
            'python_installed': False,
            'python_path': None,
            'python_version': None,
            'pip_installed': False,
            'pip_path': None
        }
        
        # Check for Python
        python_commands = ['python', 'py', 'python3']
        for cmd in python_commands:
            python_path = shutil.which(cmd)
            if python_path:
                try:
                    # Get Python version
                    version_result = subprocess.run(
                        [cmd, '--version'], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    if version_result.returncode == 0:
                        result['python_installed'] = True
                        result['python_path'] = python_path
                        result['python_version'] = version_result.stdout.strip()
                        break
                except:
                    continue
        
        # Check for pip
        if result['python_installed']:
            pip_commands = ['pip', 'pip3']
            for cmd in pip_commands:
                pip_path = shutil.which(cmd)
                if pip_path:
                    try:
                        pip_result = subprocess.run(
                            [cmd, '--version'], 
                            capture_output=True, 
                            text=True, 
                            timeout=5
                        )
                        if pip_result.returncode == 0:
                            result['pip_installed'] = True
                            result['pip_path'] = pip_path
                            break
                    except:
                        continue
        
        return result
    
    def check_ytdlp_installation(self) -> Dict[str, Any]:
        """Check yt-dlp installation status"""
        result = {
            'ytdlp_installed': False,
            'ytdlp_path': None,
            'ytdlp_version': None,
            'is_latest': False
        }
        
        # Check for yt-dlp
        ytdlp_path = shutil.which('yt-dlp')
        if ytdlp_path:
            try:
                version_result = subprocess.run(
                    ['yt-dlp', '--version'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if version_result.returncode == 0:
                    result['ytdlp_installed'] = True
                    result['ytdlp_path'] = ytdlp_path
                    result['ytdlp_version'] = version_result.stdout.strip()
                    
                    # Check if it can download (simple test for 403 errors)
                    try:
                        test_result = subprocess.run(
                            ['yt-dlp', '--simulate', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'], 
                            capture_output=True, 
                            text=True, 
                            timeout=15
                        )
                        result['is_latest'] = test_result.returncode == 0
                    except:
                        result['is_latest'] = False
            except:
                pass
        
        return result
    
    def get_setup_status(self) -> Dict[str, Any]:
        """Get complete setup status"""
        python_status = self.check_python_installation()
        ytdlp_status = self.check_ytdlp_installation()
        
        return {
            'setup_complete': self.is_setup_complete(),
            'python': python_status,
            'ytdlp': ytdlp_status,
            'needs_setup': not (python_status['python_installed'] and 
                              python_status['pip_installed'] and 
                              ytdlp_status['ytdlp_installed'] and 
                              ytdlp_status['is_latest'])
        }
    
    def should_show_setup(self) -> bool:
        """Determine if setup dialog should be shown"""
        if self.is_setup_complete():
            # Even if marked complete, check if yt-dlp is working
            ytdlp_status = self.check_ytdlp_installation()
            return not (ytdlp_status['ytdlp_installed'] and ytdlp_status['is_latest'])
        
        # First time - check if setup is needed
        status = self.get_setup_status()
        return status['needs_setup']

class SetupDialog:
    """Setup assistant dialog window"""
    
    def __init__(self, parent_window, setup_assistant: SetupAssistant):
        self.parent = parent_window
        self.setup_assistant = setup_assistant
        self.dialog = None
        self.setup_status = setup_assistant.get_setup_status()
    
    def show(self):
        """Show the setup dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("SHTxd Clip - Setup Assistant")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # Make it modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="🎬 SHTxd Clip - First Time Setup",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=config.UI_COLORS['primary']
        )
        title.pack(pady=(0, 20))
        
        # Description
        desc = ctk.CTkLabel(
            main_frame,
            text="SHTxd Clip needs Python and yt-dlp to download videos.\nLet's get you set up!",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        desc.pack(pady=(0, 30))
        
        # Step 1: Python
        self.create_python_section(main_frame)
        
        # Step 2: yt-dlp
        self.create_ytdlp_section(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
    
    def create_python_section(self, parent):
        """Create Python installation section"""
        python_frame = ctk.CTkFrame(parent, corner_radius=15)
        python_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkFrame(python_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        step_label = ctk.CTkLabel(
            header,
            text="Step 1: Python Installation",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        step_label.pack(anchor="w")
        
        # Status
        python_status = self.setup_status['python']
        if python_status['python_installed']:
            status_text = f"✅ Python installed: {python_status['python_version']}"
            status_color = "green"
        else:
            status_text = "❌ Python not found"
            status_color = "red"
        
        status_label = ctk.CTkLabel(
            python_frame,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        status_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        if not python_status['python_installed']:
            # Instructions
            instructions = ctk.CTkLabel(
                python_frame,
                text="1. Download Python from python.org\n2. ✅ CHECK 'Add to PATH' during installation\n3. Restart SHTxd Clip after installation",
                font=ctk.CTkFont(size=12),
                anchor="w",
                justify="left"
            )
            instructions.pack(anchor="w", padx=20, pady=(0, 15))
            
            # Download button
            download_btn = ctk.CTkButton(
                python_frame,
                text="📥 Download Python",
                command=self.open_python_download,
                height=40,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=config.UI_COLORS['primary']
            )
            download_btn.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_ytdlp_section(self, parent):
        """Create yt-dlp installation section"""
        ytdlp_frame = ctk.CTkFrame(parent, corner_radius=15)
        ytdlp_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header = ctk.CTkFrame(ytdlp_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        step_label = ctk.CTkLabel(
            header,
            text="Step 2: yt-dlp Installation",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        step_label.pack(anchor="w")
        
        # Status
        ytdlp_status = self.setup_status['ytdlp']
        python_status = self.setup_status['python']
        
        if ytdlp_status['ytdlp_installed'] and ytdlp_status['is_latest']:
            status_text = f"✅ yt-dlp ready: {ytdlp_status['ytdlp_version']}"
            status_color = "green"
        elif ytdlp_status['ytdlp_installed']:
            status_text = f"⚠️ yt-dlp needs update: {ytdlp_status['ytdlp_version']}"
            status_color = "orange"
        else:
            status_text = "❌ yt-dlp not found"
            status_color = "red"
        
        status_label = ctk.CTkLabel(
            ytdlp_frame,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        status_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        if not python_status['python_installed']:
            # Python required first
            requirement_label = ctk.CTkLabel(
                ytdlp_frame,
                text="⚠️ Install Python first",
                font=ctk.CTkFont(size=12),
                text_color="orange"
            )
            requirement_label.pack(anchor="w", padx=20, pady=(0, 20))
        else:
            # Instructions
            instructions = ctk.CTkLabel(
                ytdlp_frame,
                text="Open PowerShell and run this command:",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            instructions.pack(anchor="w", padx=20, pady=(0, 10))
            
            # Command box
            command_frame = ctk.CTkFrame(ytdlp_frame, fg_color=["#f0f0f0", "#2b2b2b"])
            command_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            command_text = ctk.CTkLabel(
                command_frame,
                text="pip install --upgrade yt-dlp",
                font=ctk.CTkFont(family="Consolas", size=12),
                anchor="w"
            )
            command_text.pack(anchor="w", padx=15, pady=10)
            
            # Buttons
            button_frame = ctk.CTkFrame(ytdlp_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            copy_btn = ctk.CTkButton(
                button_frame,
                text="📋 Copy Command",
                command=self.copy_command,
                width=140,
                height=35,
                font=ctk.CTkFont(size=11)
            )
            copy_btn.pack(side="left", padx=(0, 10))
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        # Check Again button
        check_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Check Again",
            command=self.check_again,
            height=45,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=config.UI_COLORS['success']
        )
        check_btn.pack(side="left", padx=(0, 10))
        
        # Skip button
        skip_btn = ctk.CTkButton(
            button_frame,
            text="⏭️ Skip Setup",
            command=self.skip_setup,
            height=45,
            width=120,
            font=ctk.CTkFont(size=12),
            fg_color=config.UI_COLORS['secondary']
        )
        skip_btn.pack(side="left", padx=(0, 10))
        
        # Done button
        done_btn = ctk.CTkButton(
            button_frame,
            text="✅ I'm Ready!",
            command=self.mark_complete,
            height=45,
            width=120,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=config.UI_COLORS['primary']
        )
        done_btn.pack(side="right")
    
    def open_python_download(self):
        """Open Python download page"""
        webbrowser.open("https://www.python.org/downloads/")
    
    def copy_command(self):
        """Copy pip command to clipboard"""
        try:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append("pip install --upgrade yt-dlp")
            messagebox.showinfo("Copied", "Command copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard: {e}")
    
    def open_powershell(self):
        """Open PowerShell"""
        try:
            subprocess.run(['powershell'], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PowerShell: {e}")
    
    def check_again(self):
        """Re-check setup status"""
        self.setup_status = self.setup_assistant.get_setup_status()
        
        # Close and recreate dialog with updated status
        self.dialog.destroy()
        self.show()
    
    def skip_setup(self):
        """Skip setup for now"""
        if messagebox.askyesno("Skip Setup", 
                             "Skip setup for now? The app may not work properly without proper installation."):
            self.dialog.destroy()
    
    def mark_complete(self):
        """Mark setup as complete"""
        status = self.setup_assistant.get_setup_status()
        if status['needs_setup']:
            messagebox.showwarning("Setup Incomplete", 
                                 "Please complete all setup steps first!")
            return
        
        self.setup_assistant.mark_setup_complete()
        messagebox.showinfo("Setup Complete", "Great! SHTxd Clip is ready to use!")
        self.dialog.destroy()
