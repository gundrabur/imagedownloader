#!/usr/bin/env python3
"""
Media Downloader GUI - macOS Application
A simple GUI wrapper for the media downloader script.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from datetime import datetime
from pathlib import Path

# Import the main functionality from the original script
import imagedownloader

class MediaDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Downloader")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.is_downloading = False
        
        # Set default output directory
        self.output_dir_var.set(str(Path.home() / "Downloads"))
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Media Downloader", 
                               font=('SF Pro Display', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="Website URL:", font=('SF Pro Display', 12)).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, 
                                  font=('SF Pro Display', 11), width=50)
        self.url_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Output directory
        ttk.Label(main_frame, text="Download Folder:", font=('SF Pro Display', 12)).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var,
                                  font=('SF Pro Display', 11))
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).grid(
            row=0, column=1)
        
        # Download button
        self.download_btn = ttk.Button(main_frame, text="Download Media Files",
                                      command=self.start_download, style='Accent.TButton')
        self.download_btn.grid(row=5, column=0, columnspan=2, pady=15)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                     font=('SF Pro Display', 10))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
        # Results text area
        ttk.Label(main_frame, text="Download Log:", font=('SF Pro Display', 12)).grid(
            row=8, column=0, sticky=tk.W, pady=(10, 5))
        
        self.log_text = tk.Text(main_frame, height=12, width=70, font=('SF Mono', 10))
        self.log_text.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar for text area
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=9, column=2, sticky=(tk.N, tk.S), pady=(0, 10))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(9, weight=1)
        
        # Example URL placeholder
        self.url_entry.insert(0, "https://example.com")
        self.url_entry.select_range(0, tk.END)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def log(self, message):
        """Add message to log text area"""
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_download(self):
        if self.is_downloading:
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a website URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "URL must start with http:// or https://")
            return
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Disable download button
        self.download_btn.configure(state='disabled')
        self.is_downloading = True
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_thread(self, url):
        try:
            # Set up the download directory
            base_dir = self.output_dir_var.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
            output_dir = os.path.join(base_dir, f"mediadownloader_{domain}_{timestamp}")
            
            # Update imagedownloader constants
            imagedownloader.BASE_URL = url
            imagedownloader.OUT_DIR = output_dir
            
            self.log(f"Starting download from: {url}")
            self.log(f"Output directory: {output_dir}")
            self.status_var.set("Fetching webpage...")
            
            # Create output directories
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
            os.makedirs(os.path.join(output_dir, 'videos'), exist_ok=True)
            os.makedirs(os.path.join(output_dir, 'audio'), exist_ok=True)
            
            # Fetch webpage
            html_bytes, ctype, err = imagedownloader.fetch(url)
            if err:
                self.log(f"ERROR: {err}")
                self.status_var.set("Error fetching webpage")
                return
            
            self.log("Parsing webpage for media files...")
            self.status_var.set("Parsing webpage...")
            
            # Parse HTML
            parser = imagedownloader.MediaExtractor()
            parser.feed(html_bytes.decode('utf-8','ignore'))
            
            # Extract candidates
            candidates = set()
            from urllib.parse import urljoin
            for u in list(parser.imgs) + list(parser.videos) + list(parser.sources) + list(parser.css_urls):
                if u and not u.lower().startswith(('data:', 'javascript:', 'about:')):
                    candidates.add(urljoin(url, u))
            
            # Regex search
            import re
            html_text = html_bytes.decode('utf-8', 'ignore')
            patterns = [
                r'(?:https?://[^"\'\s<>]*\.(?:' + '|'.join(imagedownloader.allowed_ext) + r')(?:\?[^"\'\s<>]*)?)',
                r'(?:/[^"\'\s<>]*\.(?:' + '|'.join(imagedownloader.allowed_ext) + r')(?:\?[^"\'\s<>]*)?)',
                r'["\']([^"\']*\.(?:' + '|'.join(imagedownloader.allowed_ext) + r')(?:\?[^"\']*)?)["\']',
                r'data-[^=]*=["\']([^"\']*\.(?:' + '|'.join(imagedownloader.allowed_ext) + r')(?:\?[^"\']*)?)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_text, re.IGNORECASE)
                for match in matches:
                    match_url = match if isinstance(match, str) else match[0] if match else ''
                    if match_url and not match_url.lower().startswith(('data:', 'javascript:', 'about:')):
                        candidates.add(urljoin(url, match_url))
            
            # Filter valid media URLs
            media_urls = set()
            for u in candidates:
                try:
                    p = urlparse(u)
                    if not p.scheme:
                        continue
                    path = p.path or ''
                    ext = path.rsplit('.',1)[-1].lower() if '.' in path.rsplit('/',1)[-1] else ''
                    if ext in imagedownloader.allowed_ext:
                        media_urls.add(u)
                except Exception:
                    continue
            
            total_files = len(media_urls)
            if total_files == 0:
                self.log("No media files found on the webpage")
                self.status_var.set("No media files found")
                return
            
            self.log(f"Found {total_files} media files to download")
            self.status_var.set(f"Downloading {total_files} files...")
            
            # Download files
            count_ok = 0
            count_err = 0
            
            for i, file_url in enumerate(sorted(media_urls)):
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                
                # Download file
                data, ctype, err = imagedownloader.fetch(file_url)
                if err or not data:
                    count_err += 1
                    self.log(f"Error downloading {os.path.basename(file_url)}: {err or 'No data'}")
                    continue
                
                # Determine file info
                fname = os.path.basename(urlparse(file_url).path) or 'file'
                fname = fname.split('?')[0].split('#')[0]
                
                if '.' in fname:
                    ext = fname.rsplit('.', 1)[1].lower()
                else:
                    ext = 'unknown'
                
                category = imagedownloader.get_file_category(ext)
                if not category:
                    count_err += 1
                    continue
                
                # Save file
                safe_fname = re.sub(r'[^A-Za-z0-9._-]', '_', fname)
                local_path = os.path.join(output_dir, category, safe_fname)
                
                # Handle duplicates
                if os.path.exists(local_path):
                    import hashlib
                    h = hashlib.sha1(file_url.encode()).hexdigest()[:8]
                    name_part, ext_part = os.path.splitext(safe_fname)
                    safe_fname = f"{name_part}_{h}{ext_part}"
                    local_path = os.path.join(output_dir, category, safe_fname)
                
                try:
                    with open(local_path, 'wb') as f:
                        f.write(data)
                    count_ok += 1
                    self.log(f"Downloaded: {safe_fname}")
                except Exception as e:
                    count_err += 1
                    self.log(f"Error saving {safe_fname}: {e}")
            
            self.progress_var.set(100)
            self.log(f"\nDownload complete!")
            self.log(f"Successfully downloaded: {count_ok} files")
            self.log(f"Errors: {count_err}")
            self.log(f"Output folder: {output_dir}")
            self.status_var.set(f"Complete: {count_ok} files downloaded")
            
            # Open output folder
            os.system(f'open "{output_dir}"')
            
        except Exception as e:
            self.log(f"ERROR: {e}")
            self.status_var.set("Download failed")
        finally:
            self.download_btn.configure(state='normal')
            self.is_downloading = False

def main():
    root = tk.Tk()
    
    # Set macOS-style appearance
    try:
        # Try to use native macOS appearance
        root.tk.call('source', os.path.join(os.path.dirname(__file__), 'theme.tcl'))
    except:
        pass
    
    app = MediaDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()