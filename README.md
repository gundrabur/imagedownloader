# Media Downloader

A Python script that downloads images, videos, and audio files from any webpage with an organized folder structure and progress tracking.

## Features

- **Media-focused**: Downloads only images, videos, and audio files
- **Organized structure**: Saves files in dedicated folders (images/, videos/, audio/)
- **Progress tracking**: Shows a visual progress bar during downloads
- **Smart categorization**: Automatically categorizes files by type
- **Duplicate handling**: Handles duplicate filenames automatically
- **Timestamped folders**: Creates unique folders for each download session
- **Summary reporting**: Provides detailed download statistics

## Supported File Types

- **Images**: jpg, jpeg, png, gif, webp, svg, avif, tiff, tif, bmp, ico
- **Videos**: mp4, webm, ogv, mov, avi, wmv, flv, mkv, mpg, mpeg, m4v
- **Audio**: mp3, wav, ogg, aac, flac, m4a, wma, opus

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. The script uses only standard library modules, so no additional packages are required.

## Usage

### Command line with URL argument:
```bash
python imagedownloader.py https://example.com
```

### Interactive mode (will prompt for URL):
```bash
python imagedownloader.py
```

## Output

The script creates a timestamped directory in your Downloads folder with organized subfolders:

```
imagedownloader_[domain]_[timestamp]/
├── images/          # All image files
├── videos/          # All video files  
├── audio/           # All audio files
└── manifest.json    # Detailed download information
```

Example folder: `imagedownloader_example.com_20250926_113017`

### Progress Display
During download, you'll see a real-time progress bar:
```
Progress: |████████████████████████████████████████| 25/25 (100.0%)
```

### Summary Report
After completion, the script shows:
- Total files downloaded by category
- Error count and success rate
- Output folder location
- Manifest file location

## Configuration

The script automatically saves files to your Downloads folder in a timestamped subdirectory.
You can modify these constants in the script:
- `UA` - User-Agent string
- `TIMEOUT` - Request timeout in seconds
- `allowed_ext` - Set of supported file extensions

The Downloads folder is automatically detected for the active user.

## License

This script is for educational purposes. Please respect websites' robots.txt and terms of service.