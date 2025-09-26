# 📱 Compiling Media Downloader to macOS Native App

This guide provides complete instructions for compiling the Python Media Downloader script into a native macOS application. Follow these steps whenever you make changes to `imagedownloader.py`.

## 🎯 Quick Start

If you just want to build the app immediately:

```bash
./compile_macos_app.sh
```

The script will automatically handle everything and create a ready-to-distribute app.

## 📋 Prerequisites

### System Requirements
- **macOS 10.13 or later** (for building and running)
- **Python 3.7+** installed on your system
- **Internet connection** (for downloading dependencies)
- **~50MB free disk space** (for build files)

### Check Your Setup
```bash
# Verify Python 3 is installed
python3 --version

# Verify you're on macOS
sw_vers
```

## 🛠️ Manual Compilation Steps

If you prefer to understand each step or customize the build process:

### 1. **Setup Build Environment**
```bash
# Navigate to project directory
cd /path/to/imagedownloader

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install PyInstaller
pip install pyinstaller
```

### 2. **Build Console Executable**
```bash
# Clean previous builds
rm -rf build dist *.spec

# Build standalone executable
pyinstaller --onefile --name="MediaDownloader" imagedownloader.py

# Test the executable
./dist/MediaDownloader https://example.com
```

### 3. **Create macOS App Bundle**
```bash
# Create app structure
mkdir -p "Media Downloader.app/Contents/MacOS"
mkdir -p "Media Downloader.app/Contents/Resources"

# Copy executable
cp dist/MediaDownloader "Media Downloader.app/Contents/MacOS/"

# Create GUI wrapper (see full script for complete code)
# Create Info.plist (see full script for complete plist)
```

### 4. **Deploy and Test**
```bash
# Copy to Desktop for easy access
cp -r "Media Downloader.app" ~/Desktop/

# Test the app
open "Media Downloader.app"
```

## 🔧 Automated Build Script

### Features
The `compile_macos_app.sh` script provides:

- ✅ **Prerequisite checking** - Validates Python, macOS version
- ✅ **Environment setup** - Creates/activates virtual environment  
- ✅ **Dependency management** - Installs/updates PyInstaller
- ✅ **Build cleaning** - Removes old builds automatically
- ✅ **Console executable** - Creates standalone binary
- ✅ **App bundle creation** - Builds proper .app structure
- ✅ **GUI wrapper** - Adds AppleScript-based interface
- ✅ **Testing** - Validates build integrity
- ✅ **Deployment** - Copies to Desktop automatically
- ✅ **Build reporting** - Generates detailed build info

### Usage
```bash
# Make executable (first time only)
chmod +x compile_macos_app.sh

# Run the build
./compile_macos_app.sh
```

### Build Output
```
📱 Media Downloader - macOS App Compiler
===============================================
Version: 1.0.0
Target: macOS 10.13+

▶ Checking prerequisites...
✅ Prerequisites check passed

▶ Setting up build environment...
✅ Build environment ready

▶ Cleaning previous builds...
✅ Cleanup complete

▶ Building console executable...
✅ Console executable built successfully

▶ Testing console executable...
✅ Console executable test passed

▶ Creating macOS app bundle...
✅ GUI wrapper created

▶ Installing console executable...
✅ Console executable installed

▶ Creating app icon...
✅ App icon created

▶ Validating app bundle...
✅ App bundle validation passed

▶ Testing app bundle...
✅ App bundle structure is valid

▶ Deploying app...
✅ App copied to Desktop

🎉 BUILD COMPLETED SUCCESSFULLY!
```

## 📦 Distribution

### For End Users
1. **Share** the entire `Media Downloader.app` folder
2. **Recipients** drag it to their Applications folder
3. **First launch** may require right-click → Open (security)

### File Structure
```
Media Downloader.app/
├── Contents/
│   ├── Info.plist              # App metadata
│   ├── MacOS/
│   │   ├── MediaDownloaderGUI  # GUI launcher
│   │   ├── MediaDownloader     # Console executable
│   │   └── simple_gui.py       # GUI implementation
│   └── Resources/
│       └── AppIcon.icns        # App icon (optional)
```

## 🐛 Troubleshooting

### Common Issues

**"Permission denied" when running compile script:**
```bash
chmod +x compile_macos_app.sh
```

**"PyInstaller not found":**
```bash
source .venv/bin/activate
pip install pyinstaller
```

**"Python 3 not found":**
```bash
# Install Python 3 from https://www.python.org/downloads/
# Or use Homebrew:
brew install python@3.11
```

**App won't open - "damaged or can't be verified":**
```bash
# User needs to right-click app → Open → Allow
# Or disable Gatekeeper temporarily:
sudo spctl --master-disable
```

**"No module named 'imagedownloader'":**
- Make sure `imagedownloader.py` exists in the project directory
- Check that you're running the script from the correct location

### Build Debugging

**Check build logs:**
```bash
# Build creates detailed logs
cat build_info.txt

# Check PyInstaller warnings
cat build/MediaDownloader/warn-MediaDownloader.txt
```

**Test console executable separately:**
```bash
./dist/MediaDownloader https://httpbin.org/html
```

**Validate app bundle manually:**
```bash
# Check bundle structure
find "Media Downloader.app" -type f

# Verify executable permissions  
ls -la "Media Downloader.app/Contents/MacOS/"

# Test GUI components
cd "Media Downloader.app/Contents/MacOS"
python3 simple_gui.py
```

## 🔄 Continuous Integration

### Automating Builds

For automatic building on code changes, add to your workflow:

```bash
#!/bin/bash
# auto_build.sh

# Watch for changes to imagedownloader.py
fswatch -o imagedownloader.py | while read f; do
    echo "Detected changes, rebuilding..."
    ./compile_macos_app.sh
    echo "Build complete at $(date)"
done
```

### Version Management

Update version in the compile script:
```bash
# Edit compile_macos_app.sh
APP_VERSION="1.1.0"  # Update this line
```

## 📄 Build Configuration

### Customizing the Build

Edit `compile_macos_app.sh` to modify:

- **App name:** Change `APP_NAME="Media Downloader"`
- **Bundle ID:** Change `BUNDLE_ID="com.mediadownloader.app"`  
- **Version:** Change `APP_VERSION="1.0.0"`
- **macOS target:** Change `MIN_MACOS_VERSION="10.13"`

### Advanced PyInstaller Options

For custom builds, modify the PyInstaller command:

```bash
pyinstaller \
    --onefile \
    --name="MediaDownloader" \
    --clean \
    --noconfirm \
    --add-data="config.json:." \     # Include data files
    --hidden-import=requests \       # Include hidden imports  
    --exclude-module=tkinter \       # Exclude unused modules
    imagedownloader.py
```

## 📊 Build Performance

### Typical Build Times
- **Clean build:** 30-60 seconds
- **Incremental build:** 15-30 seconds  
- **App bundle creation:** 5-10 seconds

### File Sizes
- **Console executable:** ~15-25 MB
- **Complete app bundle:** ~20-30 MB
- **Compressed distribution:** ~8-12 MB

---

## 🎯 Summary

1. **Run** `./compile_macos_app.sh` to build everything automatically
2. **Find** your app on the Desktop ready for distribution  
3. **Share** the entire `.app` folder with users
4. **Repeat** the process whenever you update `imagedownloader.py`

The compilation script handles all complexity and creates a professional, distributable macOS application that users can install and run like any native Mac app.