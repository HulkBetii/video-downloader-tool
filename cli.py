#!/usr/bin/env python3
# cli.py
"""
Command-line interface for Video Downloader Tool
"""

import argparse
import sys
import os

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from core.downloader import download_video, check_ffmpeg_available
    from utils.cookies import load_cookies_from_file
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print("Make sure you're running from the video_downloader_tool directory")
    sys.exit(1)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Video Downloader Tool - Download videos and files from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --out ./downloads
  %(prog)s --url "https://onedrive.live.com/..." --out ./downloads --cookie cookies.txt
  %(prog)s --url "video1.mp4" "video2.mp4" --out ./downloads --mode speed
  %(prog)s --headless --url "https://vimeo.com/..." --out ./downloads --verbose
        """
    )
    
    # Required arguments (except when checking ffmpeg)
    parser.add_argument(
        '--url', '-u',
        nargs='+',
        help='URL(s) to download (supports multiple URLs)'
    )
    
    parser.add_argument(
        '--out', '-o',
        help='Output directory for downloaded files'
    )
    
    # Optional arguments
    parser.add_argument(
        '--cookie', '-c',
        help='Cookie file path (.txt or .json) for authenticated downloads'
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['balanced', 'speed', 'quality'],
        default='balanced',
        help='Optimization mode (default: balanced)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--headless', '-H',
        action='store_true',
        help='Run in headless mode (no GUI)'
    )
    
    parser.add_argument(
        '--retries', '-r',
        type=int,
        default=2,
        help='Maximum number of retry attempts (default: 2)'
    )
    
    parser.add_argument(
        '--check-ffmpeg',
        action='store_true',
        help='Check ffmpeg availability and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Video Downloader Tool 1.3.0'
    )
    
    args = parser.parse_args()
    
    # Check ffmpeg if requested
    if args.check_ffmpeg:
        ffmpeg_available = check_ffmpeg_available()
        if ffmpeg_available:
            print("✅ ffmpeg is available")
            return 0
        else:
            print("❌ ffmpeg is not available")
            return 1
    
    # Validate required arguments (except when checking ffmpeg)
    if not args.url:
        parser.error("--url/-u is required")
    if not args.out:
        parser.error("--out/-o is required")
    
    # Validate output directory
    if not os.path.isdir(args.out):
        try:
            os.makedirs(args.out, exist_ok=True)
            if args.verbose:
                print(f"📁 Created output directory: {args.out}")
        except Exception as e:
            print(f"❌ Error creating output directory: {e}")
            return 1
    
    # Validate cookie file if provided
    if args.cookie and not os.path.exists(args.cookie):
        print(f"❌ Cookie file not found: {args.cookie}")
        return 1
    
    # Load cookies if provided
    cookies = {}
    if args.cookie:
        try:
            cookies = load_cookies_from_file(args.cookie)
            if args.verbose:
                print(f"🍪 Loaded {len(cookies)} cookies from {args.cookie}")
        except Exception as e:
            print(f"⚠️ Warning: Could not load cookies: {e}")
    
    # Check ffmpeg availability for quality modes
    if args.mode in ['quality']:
        ffmpeg_available = check_ffmpeg_available()
        if not ffmpeg_available:
            print("⚠️ Warning: ffmpeg not available, falling back to balanced mode")
            args.mode = 'balanced'
    
    # Status callback for CLI
    def status_callback(status_text, color="blue"):
        if args.verbose:
            print(f"[{color.upper()}] {status_text}")
        else:
            # Only show important messages in non-verbose mode
            if any(keyword in status_text.lower() for keyword in ['error', 'success', 'complete', 'failed']):
                print(status_text)
    
    # Download each URL
    success_count = 0
    total_count = len(args.url)
    
    print(f"🚀 Starting download of {total_count} URL(s) to {args.out}")
    print(f"⚙️  Mode: {args.mode}")
    if args.cookie:
        print(f"🍪 Using cookies from: {args.cookie}")
    
    for i, url in enumerate(args.url, 1):
        print(f"\n📥 Downloading {i}/{total_count}: {url}")
        
        try:
            success = download_video(
                url=url,
                output_folder=args.out,
                cookie_file=args.cookie,
                status_callback=status_callback,
                optimize_mode=args.mode,
                max_retries=args.retries
            )
            
            if success:
                success_count += 1
                print(f"✅ Successfully downloaded: {url}")
            else:
                print(f"❌ Failed to download: {url}")
                
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
    
    # Summary
    print(f"\n📊 Download Summary:")
    print(f"   Total URLs: {total_count}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 All downloads completed successfully!")
        return 0
    elif success_count > 0:
        print("⚠️ Some downloads failed")
        return 1
    else:
        print("❌ All downloads failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
