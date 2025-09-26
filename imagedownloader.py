#!/usr/bin/env python3
"""
Image and media downloader - downloads all media files from a webpage.
"""

import os
import sys
import re
import json
import hashlib
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

OUT_DIR = "downloaded_media"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TIMEOUT = 30

# Supported media file extensions
allowed_ext = {
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'avif', 'tiff', 'tif', 'bmp', 'ico',
    'mp4', 'webm', 'ogv', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'mpg', 'mpeg',
    'mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a'
}

# Create output directory
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, '_css'), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, '_js'), exist_ok=True)

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
        self.stylesheets = set()
        self.scripts = set()
        self.inline_style_urls = set()
        self.inline_script_blobs = []
        self._in_style = False
        self._in_script = False
        self._style_buf = []
        self._script_buf = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'img':
            if 'src' in a: self.imgs.add(a['src'])
            if 'srcset' in a:
                for part in a['srcset'].split(','):
                    url = part.strip().split()[0]
                    if url: self.imgs.add(url)
        if tag in ('video','audio'):
            if 'src' in a: self.videos.add(a['src'])
        if tag == 'source':
            if 'src' in a: self.sources.add(a['src'])
            if 'srcset' in a:
                for part in a['srcset'].split(','):
                    url = part.strip().split()[0]
                    if url: self.sources.add(url)
        if tag == 'link':
            rel = a.get('rel','') or a.get('REL','')
            href = a.get('href')
            if href and rel:
                rel_l = ' '.join(rel if isinstance(rel,list) else [rel]).lower()
                if 'stylesheet' in rel_l or 'preload' in rel_l:
                    self.stylesheets.add(href)
        if tag == 'script':
            src = a.get('src')
            if src:
                self.scripts.add(src)
            else:
                self._in_script = True
        if 'style' in a:
            for m in re.findall(r'url\(\s*(?:"|\')?([^"\')]+)', a['style']):
                self.inline_style_urls.add(m)
        if tag == 'style':
            self._in_style = True
    def handle_endtag(self, tag):
        if tag == 'style':
            self._in_style = False
            css = ''.join(self._style_buf)
            self._style_buf = []
            for m in re.findall(r'url\(\s*(?:"|\')?([^"\')]+)', css):
                self.inline_style_urls.add(m)
        if tag == 'script':
            if self._in_script:
                self._in_script = False
                js = ''.join(self._script_buf)
                self._script_buf = []
                self.inline_script_blobs.append(js)
    def handle_data(self, data):
        if self._in_style:
            self._style_buf.append(data)
        if self._in_script:
            self._script_buf.append(data)

# Fetch base HTML
def main():
    """Main function to download media from a webpage."""
    html_bytes, ctype, err = fetch(BASE_URL)
    if err:
        print(f'ERROR: fetching base page failed: {err}', file=sys.stderr)
        sys.exit(1)
    html_path = os.path.join(OUT_DIR, 'page.html')
    with open(html_path, 'wb') as f:
        f.write(html_bytes)

    # Parse HTML
    parser = MediaExtractor()
    parser.feed(html_bytes.decode('utf-8','ignore'))

    # Resolve stylesheet URLs
    css_urls = set()
    for href in parser.stylesheets:
        absu = urljoin(BASE_URL, href)
        css_urls.add(absu)

    # Resolve script URLs
    script_urls = set()
    for src in parser.scripts:
        absu = urljoin(BASE_URL, src)
        script_urls.add(absu)

    # Extract initial media candidates from HTML
    candidates = set()
    for u in list(parser.imgs) + list(parser.videos) + list(parser.sources) + list(parser.inline_style_urls):
        if u and not u.lower().startswith(('data:', 'javascript:', 'about:')):
            candidates.add(urljoin(BASE_URL, u))

    # Fetch and parse CSS files for url(...) refs
    css_dir = os.path.join(OUT_DIR, '_css')
    css_found_urls = set()
    for cu in sorted(css_urls):
        data, ctype, err = fetch(cu)
        name = urlparse(cu).path.split('/')[-1] or 'style.css'
        safe_name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
        save_path = os.path.join(css_dir, safe_name)
        if data:
            with open(save_path, 'wb') as f:
                f.write(data)
            text = data.decode('utf-8','ignore')
            for m in re.findall(r'url\(\s*(?:"|\')?([^"\')]+)', text):
                if m and not m.lower().startswith(('data:', 'javascript:', 'about:')):
                    css_found_urls.add(urljoin(cu, m))

    # Fetch and parse JS files for media-like URLs
    js_dir = os.path.join(OUT_DIR, '_js')
    js_found_urls = set()
    js_url_pattern = re.compile(r"[\"']([^\"']+?\.(?:" + '|'.join(sorted(allowed_ext)) + "))[\"']", re.IGNORECASE)
    for ju in sorted(script_urls):
        data, ctype, err = fetch(ju)
        name = urlparse(ju).path.split('/')[-1] or 'script.js'
        safe_name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
        save_path = os.path.join(js_dir, safe_name)
        if data:
            with open(save_path, 'wb') as f:
                f.write(data)
            text = data.decode('utf-8','ignore')
            for m in js_url_pattern.findall(text):
                if m and not str(m).lower().startswith(('data:', 'javascript:', 'about:')):
                    js_found_urls.add(urljoin(ju, m))

    # Also scan inline scripts
    for js in parser.inline_script_blobs:
        for m in js_url_pattern.findall(js):
            if m and not str(m).lower().startswith(('data:', 'javascript:', 'about:')):
                js_found_urls.add(urljoin(BASE_URL, m))

    # Combine
    all_urls = set(candidates) | set(css_found_urls) | set(js_found_urls)

    # Normalize and filter by extension when available
    media_urls = set()
    for u in all_urls:
        p = urlparse(u)
        path = p.path or ''
        ext = path.rsplit('.',1)[-1].lower() if '.' in path.rsplit('/',1)[-1] else ''
        if ext in allowed_ext or not ext:
            media_urls.add(u)

    # Download media
    manifest = []
    count_ok = 0
    count_err = 0

    def ext_from_ctype(ct):
        if not ct: return ''
        ct = ct.split(';',1)[0].strip().lower()
        mapping = {
            'image/jpeg': '.jpg', 'image/jpg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
            'image/webp': '.webp', 'image/svg+xml': '.svg', 'image/avif': '.avif', 'image/tiff': '.tif',
            'image/bmp': '.bmp', 'image/x-icon': '.ico', 'video/mp4': '.mp4', 'video/webm': '.webm',
            'video/ogg': '.ogv', 'video/quicktime': '.mov', 'video/mpeg': '.mpg'
        }
        return mapping.get(ct, '')

    for u in sorted(media_urls):
        p = urlparse(u)
        if not p.scheme.startswith('http'):
            continue
        data, ctype, err = fetch(u)
        entry = { 'url': u, 'status': 'error' if err else 'ok', 'content_type': ctype, 'size': len(data) if data else 0, 'path': None, }
        if err or not data:
            count_err += 1
            manifest.append(entry)
            continue
        # Determine local path preserving site structure
        base_dir = os.path.join(OUT_DIR, p.netloc, os.path.dirname(p.path).lstrip('/'))
        os.makedirs(base_dir, exist_ok=True)
        fname = os.path.basename(p.path) or 'index'
        fname = fname.split('?')[0].split('#')[0]
        if not fname:
            fname = 'file'
        if '.' not in fname:
            ext = ext_from_ctype(ctype)
            fname = fname + (ext or '')
        local_path = os.path.join(base_dir, fname)
        if os.path.exists(local_path):
            h = hashlib.sha1(u.encode()).hexdigest()[:8]
            root, dot, ext = fname.partition('.')
            if dot:
                fname2 = f"{root}-{h}.{ext}"
            else:
                fname2 = f"{fname}-{h}"
            local_path = os.path.join(base_dir, fname2)
        with open(local_path, 'wb') as f:
            f.write(data)
        entry['path'] = os.path.relpath(local_path, OUT_DIR)
        count_ok += 1
        manifest.append(entry)

    man_path = os.path.join(OUT_DIR, 'manifest.json')
    with open(man_path, 'w', encoding='utf-8') as f:
        json.dump({
            'base_url': BASE_URL,
            'output_dir': OUT_DIR,
            'saved': count_ok,
            'errors': count_err,
            'items': manifest,
        }, f, ensure_ascii=False, indent=2)

    print(f"Saved {count_ok} media files, {count_err} errors.\nOutput: {OUT_DIR}\nManifest: {man_path}")


if __name__ == "__main__":
    main()
