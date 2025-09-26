#!/usr/bin/env python3
"""
Simple GUI for Media Downloader using built-in modules
"""

import os
import sys
import subprocess
import tempfile
from urllib.parse import urlparse

def get_user_input():
    """Get URL from user via AppleScript dialog"""
    applescript = '''
    display dialog "Enter website URL to download media from:" default answer "https://" with title "Media Downloader"
    return text returned of result
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def show_message(title, message):
    """Show a message dialog using AppleScript"""
    applescript = f'''
    display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"
    '''
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
    except subprocess.CalledProcessError:
        print(f"{title}: {message}")

def main():
    """Main GUI function"""
    # Get URL from user
    url = get_user_input()
    if not url:
        return
    
    if not url.startswith(('http://', 'https://')):
        show_message("Error", "URL must start with http:// or https://")
        return
    
    # Show progress dialog
    applescript = '''
    display dialog "Downloading media files..." & return & "This may take a few minutes..." with title "Media Downloader" buttons {"Cancel"} giving up after 1
    '''
    subprocess.Popen(['osascript', '-e', applescript])
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for the imagedownloader module
    imagedownloader_path = None
    for filename in ['imagedownloader.py', 'MediaDownloader']:
        path = os.path.join(script_dir, filename)
        if os.path.exists(path):
            imagedownloader_path = path
            break
    
    if not imagedownloader_path:
        show_message("Error", "Media downloader not found!")
        return
    
    try:
        # Run the downloader
        if imagedownloader_path.endswith('.py'):
            result = subprocess.run([sys.executable, imagedownloader_path, url], 
                                  capture_output=True, text=True, timeout=300)
        else:
            result = subprocess.run([imagedownloader_path, url], 
                                  capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Parse output to find download directory
            output_lines = result.stdout.split('\n')
            output_dir = None
            for line in output_lines:
                if line.startswith('Output directory:'):
                    output_dir = line.split(':', 1)[1].strip()
                    break
                elif '📂 Output:' in line:
                    output_dir = line.split('📂 Output:', 1)[1].strip()
                    break
            
            if output_dir and os.path.exists(output_dir):
                # Open the download folder
                subprocess.run(['open', output_dir])
                show_message("Download Complete", 
                           f"Media files downloaded successfully!\\n\\nFiles saved to:\\n{output_dir}")
            else:
                show_message("Download Complete", "Download finished, but couldn't locate output folder.")
        else:
            error_msg = result.stderr or "Unknown error occurred"
            show_message("Download Error", f"Failed to download media files:\\n\\n{error_msg}")
    
    except subprocess.TimeoutExpired:
        show_message("Timeout", "Download took too long and was cancelled.")
    except Exception as e:
        show_message("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()