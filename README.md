# Image Downloader

A Python script that downloads all media files (images, videos, audio) from a webpage, including files referenced in CSS and JavaScript.

## Features

- Downloads images (jpg, png, gif, webp, svg, etc.)
- Downloads videos (mp4, webm, mov, etc.)
- Downloads audio files (mp3, wav, ogg, etc.)
- Parses CSS files for background images and other media references
- Scans JavaScript files for media URLs
- Preserves directory structure from the original website
- Generates a detailed manifest of all downloaded files
- Handles duplicate filenames automatically

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

The script creates a `downloaded_media` directory containing:
- `page.html` - The original HTML page
- `_css/` - Downloaded CSS files
- `_js/` - Downloaded JavaScript files
- `[domain]/` - Media files organized by domain and path
- `manifest.json` - Detailed information about all downloads

## Configuration

You can modify these constants in the script:
- `OUT_DIR` - Output directory name
- `UA` - User-Agent string
- `TIMEOUT` - Request timeout in seconds
- `allowed_ext` - Set of supported file extensions

## License

This script is for educational purposes. Please respect websites' robots.txt and terms of service.