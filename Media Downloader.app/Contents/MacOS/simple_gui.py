#!/usr/bin/env python3
"""
Simple GUI for Media Downloader using AppleScript dialogs
"""

import os
import sys
import subprocess
import tempfile
from urllib.parse import urlparse

def get_user_input():
    """Get URL from user via AppleScript dialog"""
    applescript = '''
    display dialog "Enter website URL to download media from:" default answer "https://" with title "Media Downloader" with icon note
    return text returned of result
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def show_message(title, message, icon="note"):
    """Show a message dialog using AppleScript"""
    applescript = f'''
    display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" with icon {icon}
    '''
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
    except subprocess.CalledProcessError:
        print(f"{title}: {message}")

def show_progress():
    """Show progress dialog"""
    applescript = '''
    display dialog "Downloading media files..." & return & "This may take a few minutes..." with title "Media Downloader" buttons {"Cancel"} giving up after 2 with icon note
    '''
    try:
        subprocess.Popen(['osascript', '-e', applescript])
    except:
        pass

def main():
    """Main GUI function"""
    # Get URL from user
    url = get_user_input()
    if not url:
        return
    
    if not url.startswith(('http://', 'https://')):
        show_message("Error", "URL must start with http:// or https://", "stop")
        return
    
    # Show progress
    show_progress()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for the MediaDownloader executable
    downloader_path = os.path.join(script_dir, 'MediaDownloader')
    
    if not os.path.exists(downloader_path):
        show_message("Error", "Media downloader executable not found!", "stop")
        return
    
    try:
        # Run the downloader with a reasonable timeout
        result = subprocess.run([downloader_path, url], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            # Parse output to find download directory
            output_lines = result.stdout.split('\n')
            output_dir = None
            files_downloaded = 0
            
            for line in output_lines:
                if line.startswith('Output directory:'):
                    output_dir = line.split(':', 1)[1].strip()
                elif '📁 Saved' in line and 'media files' in line:
                    # Extract number of files downloaded
                    try:
                        files_downloaded = int(line.split('📁 Saved ')[1].split(' ')[0])
                    except:
                        files_downloaded = 0
                elif 'Saved' in line and 'media files' in line:
                    try:
                        files_downloaded = int(line.split('Saved ')[1].split(' ')[0])
                    except:
                        files_downloaded = 0
            
            if output_dir and os.path.exists(output_dir):
                # Open the download folder
                subprocess.run(['open', output_dir])
                if files_downloaded > 0:
                    show_message("Download Complete ✅", 
                               f"Successfully downloaded {files_downloaded} media files!\\n\\nFiles saved to:\\n{os.path.basename(output_dir)}")
                else:
                    show_message("Download Complete", 
                               f"Download finished!\\n\\nOutput folder: {os.path.basename(output_dir)}")
            else:
                show_message("Download Complete", "Download finished successfully!")
        else:
            error_msg = result.stderr or result.stdout or "Unknown error occurred"
            # Clean up error message for user display
            if "No media files found" in error_msg:
                show_message("No Media Found", "No media files were found on this webpage.\\n\\nThis could mean:\\n• The site loads content with JavaScript\\n• No supported media files are present", "caution")
            else:
                show_message("Download Error", f"An error occurred during download:\\n\\n{error_msg[:200]}", "stop")
    
    except subprocess.TimeoutExpired:
        show_message("Timeout", "Download took too long and was cancelled.\\n\\nTry again with a smaller webpage or check your internet connection.", "caution")
    except Exception as e:
        show_message("Error", f"An unexpected error occurred:\\n\\n{str(e)}", "stop")

if __name__ == "__main__":
    main()
