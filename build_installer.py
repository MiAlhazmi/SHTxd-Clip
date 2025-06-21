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

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

def download_ffmpeg():
    """Download FFmpeg for bundling"""
    print("📥 Downloading FFmpeg...")
    
    # FFmpeg download URLs
    ffmpeg_urls = {
        'windows': 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
        'macos': 'https://evermeet.cx/ffmpeg/getrelease/zip',
        'linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
    }
    
    # For now, we'll assume Windows. You can extend this for other platforms
    if sys.platform == 'win32':
        print("⏭️  Please manually download FFmpeg from:")
        print("   https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip")
        print("   Extract ffmpeg.exe to the project directory")
        print("   Then re-run this script")
        
        if not os.path.exists('ffmpeg.exe'):
            print("❌ ffmpeg.exe not found in current directory")
            return False
    
    return True

def create_executable():
    """Create standalone executable with PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'SHTxd Clip',
        '--distpath', 'dist',
        '--workpath', 'build',
        '--specpath', 'build',
    ]
    
    # Add FFmpeg if it exists
    if os.path.exists('ffmpeg.exe'):
        cmd.extend(['--add-binary', 'ffmpeg.exe;.'])
    
    # Add icon if it exists
    if os.path.exists('app_icon.ico'):
        cmd.extend(['--icon', 'app_icon.ico'])
    
    # Add version info
    cmd.extend([
        '--add-data', 'config.py;.',
        '--add-data', 'utils.py;.',
        '--add-data', 'core.py;.',
        '--add-data', 'ui.py;.',
        'main.py'
    ])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def create_nsis_script():
    """Create NSIS installer script"""
    print("📝 Creating NSIS installer script...")
    
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
!define MUI_ICON "app_icon.ico"
!define MUI_UNICON "app_icon.ico"

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
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    print("✅ NSIS script created!")
    return True

def create_license_file():
    """Create a simple license file"""
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
    
    with open('LICENSE.txt', 'w') as f:
        f.write(license_text)
    
    print("✅ License file created!")

def build_installer():
    """Build the NSIS installer"""
    print("🔨 Building NSIS installer...")
    
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
    
    try:
        result = subprocess.run([nsis_exe, 'installer.nsi'], 
                              check=True, capture_output=True, text=True)
        print("✅ NSIS installer created successfully!")
        print(f"📦 Installer: SHTxd-Clip-Setup-v{config.APP_VERSION}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ NSIS build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build process"""
    print(f"🚀 Building SHTxd Clip v{config.APP_VERSION} installer...")
    print("=" * 50)
    
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
    
    print("=" * 50)
    print("🎉 Build completed successfully!")
    print(f"📦 Installer: SHTxd-Clip-Setup-v{config.APP_VERSION}.exe")
    print("📁 Files created:")
    print(f"   - dist/SHTxd Clip.exe (standalone executable)")
    print(f"   - SHTxd-Clip-Setup-v{config.APP_VERSION}.exe (installer)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
