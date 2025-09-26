# Media Downloader - macOS Native App

A native macOS application that downloads images, videos, and audio files from any website.

## Installation

1. **Download** the `Media Downloader.app` 
2. **Drag** it to your Applications folder
3. **Right-click** and select "Open" (first time only, due to security)
4. **Allow** the app in System Preferences > Security & Privacy if prompted

## Usage

1. **Launch** the app from Applications or Launchpad
2. **Enter** a website URL when prompted
3. **Wait** for the download to complete
4. **Check** your Downloads folder - files are organized in timestamped folders

## Features

- ✨ **Simple Interface**: Easy-to-use dialog prompts
- 🎨 **Professional Icon**: High-resolution app icon for all macOS versions
- 📁 **Organized Downloads**: Files sorted into images/, videos/, and audio/ folders  
- 🚀 **Fast Downloads**: Multi-threaded downloading with progress tracking
- 🔍 **Smart Detection**: Finds media files in HTML, CSS, and JavaScript
- 📱 **Native macOS**: Built specifically for macOS with system integration

## Supported File Types

**Images**: jpg, jpeg, png, gif, webp, svg, avif, tiff, bmp, ico
**Videos**: mp4, webm, mov, avi, wmv, flv, mkv, mpg, m4v  
**Audio**: mp3, wav, ogg, aac, flac, m4a, wma, opus

## File Organization

Downloads are saved to:
```
~/Downloads/mediadownloader_[domain]_[timestamp]/
├── images/     # All image files
├── videos/     # All video files
├── audio/      # All audio files
└── manifest.json  # Download details
```

## System Requirements

- macOS 10.13 or later
- Internet connection
- Disk space for downloads

## Troubleshooting

**"App can't be opened"**: Right-click the app → Open → Allow in Security settings

**"No media files found"**: The website may use JavaScript loading or have no compatible media files

**Downloads folder not opening**: Check your Downloads folder manually at `~/Downloads/`

## Privacy & Security

- No data is collected or transmitted
- All processing happens locally on your Mac  
- Downloads only the media files you request
- No tracking or analytics

---

**Version**: 1.0.0  
**Built**: 2025  
**License**: Free for personal use