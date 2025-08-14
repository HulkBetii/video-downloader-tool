#!/usr/bin/env python3
"""
Simple runner script for Video Downloader Tool
This script handles all import issues and runs the application
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    try:
        # Import and run the application
        from ui.download_ui import VideoDownloaderApp
        
        print("🎥 Starting Video Downloader Tool...")
        app = VideoDownloaderApp()
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the video_downloader_tool directory")
        print("💡 Try: python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
