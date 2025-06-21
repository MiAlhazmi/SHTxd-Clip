#!/usr/bin/env python3
"""
YouTube Downloader Pro - Main Entry Point
A modern, feature-rich YouTube video downloader with GUI
"""

import sys
import os
from pathlib import Path
from tkinter import messagebox

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    import config
    from utils import DependencyChecker
    from ui import YouTubeDownloaderUI
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required files are in the same directory:")
    print("- main.py")
    print("- config.py") 
    print("- utils.py")
    print("- core.py")
    print("- ui.py")
    sys.exit(1)

def check_dependencies():
    """Check for required system dependencies"""
    missing_deps = DependencyChecker.get_missing_dependencies()
    
    if missing_deps:
        error_msg = DependencyChecker.format_dependency_error(missing_deps)
        print("Missing Dependencies:")
        print("=" * 50)
        print(error_msg)
        print("=" * 50)
        
        # Try to show GUI error if possible
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()  # Hide root window
            messagebox.showerror("Missing Dependencies", error_msg)
            root.destroy()
        except:
            pass  # Fall back to console output
        
        return False
    
    return True

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        error_msg = f"Python 3.7+ is required. You have Python {sys.version_info.major}.{sys.version_info.minor}"
        print(f"Error: {error_msg}")
        
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Python Version Error", error_msg)
            root.destroy()
        except:
            pass
        
        return False
    
    return True

def check_required_packages():
    """Check if required Python packages are installed"""
    required_packages = [
        'customtkinter',
        'requests', 
        'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        # Map import names back to package names for pip install
        package_map = {'PIL': 'pillow'}
        install_packages = [package_map.get(pkg, pkg) for pkg in missing_packages]
        
        error_msg = f"Missing Python packages: {', '.join(install_packages)}\n\n"
        error_msg += "Install with:\n"
        error_msg += f"pip install {' '.join(install_packages)}"
        
        print("Missing Python Packages:")
        print("=" * 50) 
        print(error_msg)
        print("=" * 50)
        
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Missing Python Packages", error_msg)
            root.destroy()
        except:
            pass
        
        return False
    
    return True

def main():
    """Main entry point"""
    print(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check required Python packages
    if not check_required_packages():
        sys.exit(1)
    
    # Check system dependencies
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    print("✅ All dependencies satisfied")
    print("🚀 Starting application...")
    
    try:
        # Create and run the application
        app = YouTubeDownloaderUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        error_msg = f"Failed to start {config.APP_NAME}:\n\n{str(e)}"
        print(f"❌ Error: {error_msg}")
        
        # Show GUI error if possible
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
