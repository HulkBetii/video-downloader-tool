# main.py
import sys
import os
import argparse

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """Main entry point for Video Downloader Tool"""
    # Check if CLI arguments are provided
    if len(sys.argv) > 1:
        # Delegate to CLI
        try:
            from cli import main as cli_main
            return cli_main()
        except ImportError as e:
            print(f"Error: Could not import CLI module: {e}")
            print("Make sure you're running from the video_downloader_tool directory")
            return 1
    else:
        # Launch GUI
        try:
            from ui.views.main_window import VideoDownloaderApp
            app = VideoDownloaderApp()
            app.mainloop()
            return 0
        except ImportError as e:
            print(f"Error: Could not import VideoDownloaderApp: {e}")
            print("Make sure you're running from the video_downloader_tool directory")
            return 1
        except Exception as e:
            print(f"Error: Could not start application: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
