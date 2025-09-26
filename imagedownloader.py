#!/usr/bin/env python3
"""
Image and media downloader - downloads all media files from a webpage.
"""

import os
import sys
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

# Configuration
if len(sys.argv) < 2:
    BASE_URL = input("Enter the URL to download media from: ").strip()
    if not BASE_URL:
        print("ERROR: No URL provided", file=sys.stderr)
        sys.exit(1)
else:
    BASE_URL = sys.argv[1]

# Create timestamped folder in active user's Downloads directory
def get_downloads_folder():
    """Get the active user's Downloads folder path."""
    # Try to get user's Downloads folder
    downloads_paths = [
        Path.home() / "Downloads",  # Standard location
        Path.home() / "downloads",  # Lowercase variant
        os.path.expanduser("~/Downloads"),  # Alternative method
    ]
    
    for path in downloads_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return str(path)
    
    # Fallback to current directory if Downloads folder not found
    print("Warning: Downloads folder not found, using current directory")
    return "."

downloads_dir = get_downloads_folder()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
domain = urlparse(BASE_URL).netloc.replace('www.', '')
OUT_DIR = os.path.join(downloads_dir, f"imagedownloader_{domain}_{timestamp}")

print(f"Output directory: {OUT_DIR}")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TIMEOUT = 30

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TIMEOUT = 30

# Supported media file extensions organized by type
image_ext = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'avif', 'tiff', 'tif', 'bmp', 'ico'}
video_ext = {'mp4', 'webm', 'ogv', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'mpg', 'mpeg', 'm4v'}
audio_ext = {'mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma', 'opus'}

# All supported extensions
allowed_ext = image_ext | video_ext | audio_ext

def get_file_category(ext):
    """Determine which category a file belongs to based on its extension."""
    ext = ext.lower()
    if ext in image_ext:
        return 'images'
    elif ext in video_ext:
        return 'videos' 
    elif ext in audio_ext:
        return 'audio'
    return None

# Create output directory structure
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, 'images'), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, 'videos'), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, 'audio'), exist_ok=True)

def fetch(url):
    try:
        req = Request(url, headers={'User-Agent': UA})
        with urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
            ctype = r.headers.get('Content-Type','')
            return data, ctype, None
    except Exception as e:
        return None, None, str(e)

class MediaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs = set()
        self.videos = set()
        self.sources = set()
        
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'img':
            if 'src' in a: 
                self.imgs.add(a['src'])
            if 'srcset' in a:
                for part in a['srcset'].split(','):
                    url_parts = part.strip().split()
                    if url_parts: 
                        url = url_parts[0]
                        if url: self.imgs.add(url)
        elif tag in ('video', 'audio'):
            if 'src' in a: 
                self.videos.add(a['src'])
        elif tag == 'source':
            if 'src' in a: 
                self.sources.add(a['src'])
            if 'srcset' in a:
                for part in a['srcset'].split(','):
                    url_parts = part.strip().split()
                    if url_parts:
                        url = url_parts[0]
                        if url: self.sources.add(url)

# Fetch base HTML
def main():
    """Main function to download media from a webpage."""
    print("Fetching webpage...")
    html_bytes, ctype, err = fetch(BASE_URL)
    if err:
        print(f'ERROR: fetching base page failed: {err}', file=sys.stderr)
        sys.exit(1)

    # Parse HTML to extract media URLs
    print("Parsing HTML for media files...")
    parser = MediaExtractor()
    parser.feed(html_bytes.decode('utf-8','ignore'))

    # Extract media candidates from HTML
    candidates = set()
    for u in list(parser.imgs) + list(parser.videos) + list(parser.sources):
        if u and not u.lower().startswith(('data:', 'javascript:', 'about:')):
            candidates.add(urljoin(BASE_URL, u))

    # Filter by extension
    media_urls = set()
    for u in candidates:
        p = urlparse(u)
        path = p.path or ''
        ext = path.rsplit('.',1)[-1].lower() if '.' in path.rsplit('/',1)[-1] else ''
        if ext in allowed_ext:
            media_urls.add(u)

    if not media_urls:
        print("No media files found on the webpage.")
        return

    print(f"Found {len(media_urls)} media files to download")

    # Download media with progress bar
    manifest = []
    count_ok = 0
    count_err = 0
    
    def get_file_extension_from_content_type(ct):
        """Get file extension from content type."""
        if not ct: return ''
        ct = ct.split(';',1)[0].strip().lower()
        mapping = {
            'image/jpeg': '.jpg', 'image/jpg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
            'image/webp': '.webp', 'image/svg+xml': '.svg', 'image/avif': '.avif', 'image/tiff': '.tif',
            'image/bmp': '.bmp', 'image/x-icon': '.ico', 'video/mp4': '.mp4', 'video/webm': '.webm',
            'video/ogg': '.ogv', 'video/quicktime': '.mov', 'video/mpeg': '.mpg',
            'audio/mpeg': '.mp3', 'audio/wav': '.wav', 'audio/ogg': '.ogg'
        }
        return mapping.get(ct, '')

    media_list = sorted(media_urls)
    for i, url in enumerate(media_list):
        # Simple progress bar
        progress = (i + 1) / len(media_list)
        bar_length = 50
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f'\rProgress: |{bar}| {i + 1}/{len(media_list)} ({progress:.1%})', end='', flush=True)
        
        p = urlparse(url)
        if not p.scheme.startswith('http'):
            continue
            
        data, ctype, err = fetch(url)
        entry = {
            'url': url, 
            'status': 'error' if err else 'ok', 
            'content_type': ctype, 
            'size': len(data) if data else 0, 
            'path': None
        }
        
        if err or not data:
            count_err += 1
            manifest.append(entry)
            continue

        # Determine file extension and category
        fname = os.path.basename(p.path) or 'file'
        fname = fname.split('?')[0].split('#')[0]  # Remove query params and fragments
        
        # Get extension from filename or content type
        if '.' in fname:
            ext = fname.rsplit('.', 1)[1].lower()
        else:
            ext = get_file_extension_from_content_type(ctype).lstrip('.')
            if ext:
                fname = f"{fname}.{ext}"
            else:
                fname = f"{fname}.unknown"
                ext = 'unknown'

        # Determine category
        category = get_file_category(ext)
        if not category:
            count_err += 1
            manifest.append(entry)
            continue

        # Create safe filename and handle duplicates
        safe_fname = re.sub(r'[^A-Za-z0-9._-]', '_', fname)
        local_path = os.path.join(OUT_DIR, category, safe_fname)
        
        # Handle duplicate filenames
        if os.path.exists(local_path):
            h = hashlib.sha1(url.encode()).hexdigest()[:8]
            name_part, ext_part = os.path.splitext(safe_fname)
            safe_fname = f"{name_part}_{h}{ext_part}"
            local_path = os.path.join(OUT_DIR, category, safe_fname)

        # Save file
        try:
            with open(local_path, 'wb') as f:
                f.write(data)
            entry['path'] = os.path.join(category, safe_fname)
            count_ok += 1
        except Exception as e:
            entry['error'] = str(e)
            count_err += 1
            
        manifest.append(entry)

    print()  # New line after progress bar
    
    # Save manifest
    man_path = os.path.join(OUT_DIR, 'manifest.json')
    with open(man_path, 'w', encoding='utf-8') as f:
        json.dump({
            'base_url': BASE_URL,
            'output_dir': OUT_DIR,
            'saved': count_ok,
            'errors': count_err,
            'items': manifest,
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ Download complete!")
    print(f"📁 Saved {count_ok} media files, {count_err} errors")
    print(f"📂 Output: {OUT_DIR}")
    print(f"📄 Manifest: {man_path}")
    
    # Print summary by category
    if count_ok > 0:
        categories = {}
        for entry in manifest:
            if entry['status'] == 'ok' and entry['path']:
                cat = entry['path'].split('/')[0]
                categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Files by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} files")


if __name__ == "__main__":
    main()
