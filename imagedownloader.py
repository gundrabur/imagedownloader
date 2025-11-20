#!/usr/bin/env python3
"""
Image and media downloader - downloads all media files from a webpage.
"""

import os
import sys
import re
import json
import hashlib
import time
import gzip
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
import platform

# Configuration
if len(sys.argv) < 2:
    BASE_URL = input("Enter the URL to download media from: ").strip()
    if not BASE_URL:
        print("ERROR: No URL provided", file=sys.stderr)
        sys.exit(1)
else:
    BASE_URL = sys.argv[1]

# Create timestamped folder in active user's Downloads directory (cross-platform, including OneDrive on Windows)
def get_downloads_folder():
    """Get the active user's Downloads folder path (handles common Windows OneDrive cases)."""
    home = Path.home()

    candidates = [
        home / "Downloads",
        home / "downloads",
    ]

    # Windows specific: check OneDrive variations
    if platform.system().lower() == 'windows':
        onedrive = os.environ.get('OneDrive') or os.environ.get('ONEDRIVE')
        if onedrive:
            candidates.append(Path(onedrive) / 'Downloads')
        # Corporate managed devices sometimes have OneDrive - <OrgName>
        for env_var in ['OneDriveCommercial', 'OneDriveConsumer']:
            if os.environ.get(env_var):
                candidates.append(Path(os.environ[env_var]) / 'Downloads')

        # Windows Known Folders (fallback via USERPROFILE)
        userprofile = os.environ.get('USERPROFILE')
        if userprofile:
            candidates.append(Path(userprofile) / 'Downloads')

    for p in candidates:
        try:
            if p.exists() and p.is_dir():
                return str(p)
        except Exception:
            continue

    print("Warning: Downloads folder not found, using current directory")
    return os.getcwd()

downloads_dir = get_downloads_folder()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
domain = urlparse(BASE_URL).netloc.replace('www.', '')
OUT_DIR = os.path.join(downloads_dir, f"imagedownloader_{domain}_{timestamp}")

print(f"Output directory: {OUT_DIR}")

# User-Agent / timeout (updated to latest Chrome version)
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0.0.0 Safari/537.36"
)
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

def fetch(url, retries=2, is_main_page=False):
    """Enhanced fetch function with better headers to avoid 403 errors."""
    for attempt in range(retries + 1):
        try:
            # More comprehensive headers to appear more like a real browser
            headers = {
                'User-Agent': UA,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # Add referer for media files (not for main page)
            if not is_main_page:
                parsed_url = urlparse(url)
                headers['Referer'] = f"{parsed_url.scheme}://{parsed_url.netloc}/"
            
            req = Request(url, headers=headers)
            with urlopen(req, timeout=TIMEOUT) as r:
                data = r.read()
                ctype = r.headers.get('Content-Type','')
                
                # Handle different compression encodings
                encoding = r.headers.get('Content-Encoding', '').lower()
                if encoding == 'gzip':
                    try:
                        data = gzip.decompress(data)
                    except gzip.BadGzipFile:
                        pass  # Data wasn't actually gzipped
                elif encoding == 'deflate':
                    try:
                        import zlib
                        data = zlib.decompress(data)
                    except zlib.error:
                        pass  # Data wasn't actually deflated
                elif encoding == 'br':
                    try:
                        import brotli
                        data = brotli.decompress(data)
                    except ImportError:
                        if is_main_page:
                            print("Warning: Brotli compression detected but brotli module not available")
                    except Exception:
                        pass  # Data wasn't actually brotli compressed
                
                return data, ctype, None
                
        except HTTPError as e:
            if e.code == 403 and attempt < retries:
                print(f"  403 Forbidden, retrying ({attempt + 1}/{retries})...")
                time.sleep(1)  # Brief delay before retry
                continue
            elif e.code == 429 and attempt < retries:  # Rate limiting
                print(f"  Rate limited, waiting before retry ({attempt + 1}/{retries})...")
                time.sleep(2)
                continue
            return None, None, f"HTTP Error {e.code}: {e.reason}"
        except URLError as e:
            return None, None, f"URL Error: {e.reason}"
        except Exception as e:
            if attempt < retries:
                time.sleep(0.5)
                continue
            return None, None, str(e)
    
    return None, None, "Max retries exceeded"

class MediaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs = set()
        self.videos = set()
        self.sources = set()
        self.css_urls = set()  # For inline CSS background images
        
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
            # Check for data-src (lazy loading)
            if 'data-src' in a:
                self.imgs.add(a['data-src'])
        elif tag in ('video', 'audio'):
            if 'src' in a: 
                self.videos.add(a['src'])
            # Check for poster attribute on video tags
            if tag == 'video' and 'poster' in a:
                self.imgs.add(a['poster'])
        elif tag == 'source':
            if 'src' in a: 
                self.sources.add(a['src'])
            if 'srcset' in a:
                for part in a['srcset'].split(','):
                    url_parts = part.strip().split()
                    if url_parts:
                        url = url_parts[0]
                        if url: self.sources.add(url)
        
        # Check for inline style attributes with background images
        if 'style' in a:
            style = a['style']
            # Look for url() in CSS
            import re
            for match in re.findall(r'url\(\s*["\']?([^"\')\s]+)["\']?\s*\)', style, re.IGNORECASE):
                if match and not match.lower().startswith(('data:', 'javascript:', 'about:')):
                    self.css_urls.add(match)

# Fetch base HTML
def main():
    """Main function to download media from a webpage."""
    print("Fetching webpage...")
    html_bytes, ctype, err = fetch(BASE_URL, is_main_page=True)
    if err:
        print(f'ERROR: fetching base page failed: {err}', file=sys.stderr)
        sys.exit(1)

    # Parse HTML to extract media URLs
    print("Parsing HTML for media files...")
    parser = MediaExtractor()
    parser.feed(html_bytes.decode('utf-8','ignore'))

    # Extract media candidates from HTML
    candidates = set()
    for u in list(parser.imgs) + list(parser.videos) + list(parser.sources) + list(parser.css_urls):
        if u and not u.lower().startswith(('data:', 'javascript:', 'about:')):
            candidates.add(urljoin(BASE_URL, u))

    # Also do a simple regex search through the HTML for any URLs that look like media files
    html_text = html_bytes.decode('utf-8', 'ignore')
    print("Scanning for additional media URLs...")
    
    # Look for URLs ending with media extensions - more comprehensive patterns
    patterns = [
        # Standard URLs with extensions
        r'(?:https?://[^"\'\s<>]*\.(?:' + '|'.join(allowed_ext) + r')(?:\?[^"\'\s<>]*)?)',
        # Relative URLs with extensions  
        r'(?:/[^"\'\s<>]*\.(?:' + '|'.join(allowed_ext) + r')(?:\?[^"\'\s<>]*)?)',
        # URLs in quotes
        r'["\']([^"\']*\.(?:' + '|'.join(allowed_ext) + r')(?:\?[^"\']*)?)["\']',
        # Data attributes
        r'data-[^=]*=["\']([^"\']*\.(?:' + '|'.join(allowed_ext) + r')(?:\?[^"\']*)?)["\']'
    ]
    
    regex_found = set()
    for pattern in patterns:
        matches = re.findall(pattern, html_text, re.IGNORECASE)
        for match in matches:
            # Handle both full matches and group matches
            url = match if isinstance(match, str) else match[0] if match else ''
            if url and not url.lower().startswith(('data:', 'javascript:', 'about:')):
                regex_found.add(url)
    
    # Add regex found URLs to candidates
    for url in regex_found:
        candidates.add(urljoin(BASE_URL, url))

    print(f"Found {len(candidates)} potential media URLs")

    # Filter by extension and validate URLs
    media_urls = set()
    invalid_count = 0
    for u in candidates:
        try:
            p = urlparse(u)
            if not p.scheme:
                invalid_count += 1
                continue  # Skip invalid URLs
            path = p.path or ''
            ext = path.rsplit('.',1)[-1].lower() if '.' in path.rsplit('/',1)[-1] else ''
            if ext in allowed_ext:
                media_urls.add(u)
        except Exception:
            invalid_count += 1
            continue  # Skip malformed URLs
    
    if invalid_count > 0:
        print(f"Filtered out {invalid_count} invalid URLs")

    if not media_urls:
        print("No media files found on the webpage.")
        return

    print(f"Found {len(media_urls)} media files to download")

    # If more than 250 files, filter to only images and get the 250 largest
    if len(media_urls) > 250:
        print(f"⚠️  More than 250 files detected ({len(media_urls)} files)")
        print("📸 Filtering to images only and checking sizes...")
        
        # Filter to only image URLs based on extension
        image_urls = set()
        for u in media_urls:
            try:
                p = urlparse(u)
                path = p.path or ''
                ext = path.rsplit('.',1)[-1].lower() if '.' in path.rsplit('/',1)[-1] else ''
                if ext in image_ext:
                    image_urls.add(u)
            except Exception:
                continue
        
        if not image_urls:
            print("❌ No image files found after filtering.")
            return
        
        print(f"Found {len(image_urls)} image files")
        
        # Get file sizes for all images
        print("📏 Checking file sizes (this may take a moment)...")
        image_sizes = []
        for i, url in enumerate(sorted(image_urls)):
            # Progress indicator
            if (i + 1) % 10 == 0 or i == 0:
                print(f"  Checking {i + 1}/{len(image_urls)}...", end='\r')
            
            data, ctype, err = fetch(url)
            if data and not err:
                image_sizes.append((url, len(data)))
            time.sleep(0.05)  # Small delay to be respectful
        
        print()  # New line after progress
        
        if not image_sizes:
            print("❌ Could not determine sizes for any images.")
            return
        
        # Sort by size (largest first) and take top 250
        image_sizes.sort(key=lambda x: x[1], reverse=True)
        top_250 = image_sizes[:250]
        
        # Update media_urls to only include the top 250 largest images
        media_urls = set(url for url, size in top_250)
        
        total_size_mb = sum(size for _, size in top_250) / (1024 * 1024)
        print(f"✅ Selected 250 largest images (total size: {total_size_mb:.1f} MB)")
        print(f"   Largest: {top_250[0][1] / (1024 * 1024):.2f} MB")
        print(f"   Smallest: {top_250[-1][1] / (1024 * 1024):.2f} MB")

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

    # Choose basic progress bar characters for Windows terminal if needed
    use_simple_bar = False
    if platform.system().lower() == 'windows':
        # Heuristic: Some Windows terminals may not render block characters well
        if not os.environ.get('WT_SESSION') and 'vscode' not in os.environ.get('TERM_PROGRAM','').lower():
            use_simple_bar = True
    for i, url in enumerate(media_list):
        # Simple progress bar
        progress = (i + 1) / len(media_list)
        bar_length = 50
        filled_length = int(bar_length * progress)
        if use_simple_bar:
            bar = '#' * filled_length + '-' * (bar_length - filled_length)
        else:
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f'\rProgress: |{bar}| {i + 1}/{len(media_list)} ({progress:.1%})', end='', flush=True)
        
        p = urlparse(url)
        if not p.scheme.startswith('http'):
            continue
            
        data, ctype, err = fetch(url)
        
        # Small delay between downloads to be respectful
        if i > 0:
            time.sleep(0.1)
        entry = {
            'url': url,
            'status': 'error' if err else 'ok',
            'content_type': ctype,
            'size': len(data) if data else 0,
            'path': None,  # normalized forward-slash relative path after save
            'category': None,
            'error': err if err else None
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

        # Determine category once and store explicitly (Windows path safe)
        category = get_file_category(ext)
        if not category:
            entry['error'] = f'Unsupported file type: {ext}'
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
            entry['path'] = f"{category}/{safe_fname}"  # use forward slashes for portability
            entry['category'] = category
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
            if entry['status'] == 'ok' and entry.get('category'):
                cat = entry['category']
                categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Files by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} files")


if __name__ == "__main__":
    main()
