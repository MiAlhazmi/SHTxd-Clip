#!/usr/bin/env python3
"""
Build script for SHTxd Clip installer
Creates a standalone executable and NSIS installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import config


def get_desktop_path():
    """Get the desktop path for output"""
    desktop = Path.home() / "Desktop" / "SHTxd-Clip-Build"
    desktop.mkdir(exist_ok=True)
    return desktop


def clean_build_dirs():
    """Clean previous build directories"""
    desktop_build = get_desktop_path()

    # Clean project dirs
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

    # Clean desktop build folder
    if desktop_build.exists():
        print(f"🧹 Cleaning {desktop_build}...")
        shutil.rmtree(desktop_build)
        desktop_build.mkdir(exist_ok=True)


def download_ffmpeg():
    """Download FFmpeg for bundling"""
    print("📥 Checking for FFmpeg...")

    # Check if FFmpeg already exists
    if os.path.exists('ffmpeg.exe'):
        print("✅ FFmpeg found!")
        return True

    # Auto-download FFmpeg for Windows
    if sys.platform == 'win32':
        print("📥 Auto-downloading FFmpeg...")
        try:
            import requests
            import zipfile
            import tempfile

            # FFmpeg download URL
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

            # Download
            print("📥 Downloading FFmpeg (this may take a moment)...")
            response = requests.get(ffmpeg_url, stream=True)
            response.raise_for_status()

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_zip_path = temp_file.name

            # Extract ffmpeg.exe
            print("📦 Extracting FFmpeg...")
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                # Find ffmpeg.exe in the zip
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith('bin/ffmpeg.exe'):
                        # Extract just ffmpeg.exe to current directory
                        file_info.filename = 'ffmpeg.exe'
                        zip_ref.extract(file_info, '.')
                        break

            # Clean up temp file
            os.unlink(temp_zip_path)

            if os.path.exists('ffmpeg.exe'):
                print("✅ FFmpeg downloaded successfully!")
                return True
            else:
                print("❌ Failed to extract ffmpeg.exe")
                return False

        except Exception as e:
            print(f"❌ Failed to auto-download FFmpeg: {e}")
            print("⏭️ Please manually download FFmpeg from:")
            print(
                "   https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip")
            print("   Extract ffmpeg.exe to the project directory")
            return False
    else:
        print("⏭️ Please manually install FFmpeg for your platform")
        return False


def create_executable():
    """Create standalone executable with PyInstaller"""
    print("🔨 Building executable with PyInstaller...")

    # Update yt-dlp before building
    print("🔄 Updating yt-dlp before build...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'],
                       check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("✅ yt-dlp updated to latest version")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to update yt-dlp, continuing with current version")

    # Find CustomTkinter installation path
    try:
        import customtkinter
        ctk_path = os.path.dirname(customtkinter.__file__)
        print(f"📁 CustomTkinter path: {ctk_path}")
    except ImportError:
        print("❌ CustomTkinter not found!")
        return False

    # Find yt-dlp installation path for bundling
    try:
        import yt_dlp
        ytdlp_path = os.path.dirname(yt_dlp.__file__)
        print(f"📁 yt-dlp path: {ytdlp_path}")
    except ImportError:
        print("❌ yt-dlp not found!")
        return False

    # Set output to desktop
    desktop_build = get_desktop_path()
    dist_path = desktop_build / "dist"
    build_path = desktop_build / "build"

    # Get current project directory
    project_dir = os.getcwd()

    # PyInstaller command with all assets
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'SHTxd Clip',
        '--distpath', str(dist_path),
        '--workpath', str(build_path),
        '--specpath', str(build_path),
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'requests',
        '--hidden-import', 'PIL',
        '--hidden-import', 'packaging',
        '--hidden-import', 'yt_dlp',
        '--hidden-import', 'websockets',
        '--hidden-import', 'brotli',
        '--hidden-import', 'mutagen',
        # Add CustomTkinter assets
        '--add-data', f'{ctk_path};customtkinter/',
        # Bundle yt-dlp completely
        '--add-data', f'{ytdlp_path};yt_dlp/',
        # Include extractors
        '--collect-all', 'yt_dlp',
    ]

    # Add FFmpeg if it exists
    ffmpeg_path = os.path.join(project_dir, 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        cmd.extend(['--add-binary', f'{ffmpeg_path};.'])
        print("✅ Including FFmpeg")
    else:
        print("⚠️ FFmpeg not found - skipping")

    # Add icon if it exists (use absolute path from project directory)
    icon_path = os.path.join(project_dir, 'app_icon.ico')
    if os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
        print(f"✅ Including icon: {icon_path}")
    else:
        print("⚠️ app_icon.ico not found - building without icon")

    # Add the main script (use absolute path)
    main_script = os.path.join(project_dir, 'main.py')
    cmd.append(main_script)

    print(f"🔧 Building with latest yt-dlp bundled...")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("✅ Executable created successfully!")
        print(f"📁 Output location: {dist_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def create_nsis_script():
    """Create NSIS installer script"""
    print("📝 Creating NSIS installer script...")

    desktop_build = get_desktop_path()

    nsis_script = f'''
; SHTxd Clip Installer Script
; Generated automatically

!define APP_NAME "SHTxd Clip"
!define APP_VERSION "{config.APP_VERSION}"
!define APP_PUBLISHER "SHTxd"
!define APP_URL "https://github.com/MiAlhazmi/SHTxd-Clip"
!define APP_EXECUTABLE "SHTxd Clip.exe"

; Installer settings
Name "${{APP_NAME}} v${{APP_VERSION}}"
OutFile "SHTxd-Clip-Setup-v${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES\\SHTxd\\SHTxd Clip"
InstallDirRegKey HKLM "Software\\SHTxd\\SHTxd Clip" "InstallDir"
RequestExecutionLevel admin

; Modern UI
!include "MUI2.nsh"
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Main Application" SecMain
    SetOutPath "$INSTDIR"

    ; Copy files
    File "dist\\${{APP_EXECUTABLE}}"

    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\SHTxd"
    CreateShortcut "$SMPROGRAMS\\SHTxd\\SHTxd Clip.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    CreateShortcut "$DESKTOP\\SHTxd Clip.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"

    ; Registry entries
    WriteRegStr HKLM "Software\\SHTxd\\SHTxd Clip" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\SHTxd\\SHTxd Clip" "Version" "${{APP_VERSION}}"

    ; Uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"

    ; Add/Remove Programs entry
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "URLInfoAbout" "${{APP_URL}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "NoRepair" 1

SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\\${{APP_EXECUTABLE}}"
    Delete "$INSTDIR\\Uninstall.exe"

    ; Remove shortcuts
    Delete "$SMPROGRAMS\\SHTxd\\SHTxd Clip.lnk"
    Delete "$DESKTOP\\SHTxd Clip.lnk"
    RMDir "$SMPROGRAMS\\SHTxd"

    ; Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip"
    DeleteRegKey HKLM "Software\\SHTxd\\SHTxd Clip"

    ; Remove install directory
    RMDir "$INSTDIR"
SectionEnd

; Functions
Function .onInit
    ; Check if already installed
    ReadRegStr $R0 HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SHTxd Clip" "UninstallString"
    StrCmp $R0 "" done

    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \\
        "SHTxd Clip is already installed. $\\n$\\nClick OK to remove the previous version or Cancel to cancel this upgrade." \\
        IDOK uninst
    Abort

uninst:
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR'

done:
FunctionEnd
'''

    nsis_file = desktop_build / 'installer.nsi'
    with open(nsis_file, 'w') as f:
        f.write(nsis_script)

    print(f"✅ NSIS script created: {nsis_file}")
    return True


def create_license_file():
    """Create a simple license file"""
    desktop_build = get_desktop_path()

    license_text = f"""SHTxd Clip v{config.APP_VERSION}

Copyright (c) 2024 SHTxd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    license_file = desktop_build / 'LICENSE.txt'
    with open(license_file, 'w') as f:
        f.write(license_text)

    print(f"✅ License file created: {license_file}")


def build_installer():
    """Build the NSIS installer"""
    print("🔨 Building NSIS installer...")

    desktop_build = get_desktop_path()

    # Check if NSIS is available
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"  # If in PATH
    ]

    nsis_exe = None
    for path in nsis_paths:
        if shutil.which(path) or os.path.exists(path):
            nsis_exe = path
            break

    if not nsis_exe:
        print("❌ NSIS not found! Please install NSIS from https://nsis.sourceforge.io/Download")
        return False

    # Build installer (change to desktop directory)
    original_dir = os.getcwd()
    try:
        os.chdir(desktop_build)
        result = subprocess.run([nsis_exe, 'installer.nsi'],
                                check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("✅ NSIS installer created successfully!")
        installer_name = f"SHTxd-Clip-Setup-v{config.APP_VERSION}.exe"
        print(f"📦 Installer: {desktop_build / installer_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ NSIS build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    finally:
        os.chdir(original_dir)


def main():
    """Main build process"""
    desktop_build = get_desktop_path()

    print(f"🚀 Building SHTxd Clip v{config.APP_VERSION} installer...")
    print(f"📁 Output location: {desktop_build}")
    print("=" * 60)

    # Step 1: Clean previous builds
    clean_build_dirs()

    # Step 2: Check/download FFmpeg
    if not download_ffmpeg():
        print("⚠️  Continuing without FFmpeg (users will need to install separately)")

    # Step 3: Create executable
    if not create_executable():
        print("❌ Failed to create executable")
        return 1

    # Step 4: Create license file
    create_license_file()

    # Step 5: Create NSIS script
    if not create_nsis_script():
        print("❌ Failed to create NSIS script")
        return 1

    # Step 6: Build installer
    if not build_installer():
        print("❌ Failed to build installer")
        return 1

    print("=" * 60)
    print("🎉 Build completed successfully!")
    print(f"📁 All files saved to: {desktop_build}")
    print("📦 Files created:")
    print(f"   - dist/SHTxd Clip.exe (standalone executable)")
    print(f"   - SHTxd-Clip-Setup-v{config.APP_VERSION}.exe (installer)")
    print(f"   - LICENSE.txt")
    print("\n🚀 Ready for distribution!")

    return 0


if __name__ == "__main__":
    sys.exit(main())