# ui/controllers/download_controller.py
import threading
import os
import sys

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.downloader import download_video, check_ffmpeg_available
except ImportError:
    # Fallback for when running as script
    core_dir = os.path.join(project_root, 'core')
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)
    try:
        from downloader import download_video, check_ffmpeg_available  # type: ignore
    except ImportError:
        print("Error: Could not import required modules")
        sys.exit(1)


class DownloadController:
    """Controller for video download operations"""
    
    def __init__(self, app):
        self.app = app
        self.active_downloads = 0
    
    def start_download(self):
        """Start video download process"""
        # Get URLs from input
        urls = self.app.download_tab.video_url_input.get_urls()
        if not urls:
            self.app.download_tab.video_progress.update_status("❌ Vui lòng nhập URL video.", "red")
            return
        
        # Get output folder
        output_folder = self.app.download_tab.output_entry.get().strip()
        if not output_folder or not os.path.isdir(output_folder):
            self.app.download_tab.video_progress.update_status("❌ Vui lòng chọn thư mục lưu hợp lệ.", "red")
            return
        
        # Get cookie file
        cookie_file = self.app.download_tab.video_cookie_input.get_cookie_file()
        
        # Get optimization mode
        optimize_mode = self.app.download_tab.video_optimization.get_mode()
        
        # Start download for each URL
        for i, url in enumerate(urls, 1):
            if url.strip():
                self.run_download(url, output_folder, cookie_file, optimize_mode, i)
    
    def run_download(self, url, output_folder, cookie_file, optimize_mode, line_number):
        """Run download in separate thread"""
        def update_status(status_text, color="#3b5998"):
            self.app.download_tab.video_progress.update_status(status_text, color)
        
        def download_thread():
            try:
                self.active_downloads += 1
                self.app.download_tab.video_download_button.config(state="disabled")
                self.app.download_tab.video_progress.start_progress()
                
                update_status(f"🚀 Bắt đầu tải video {line_number}...", "blue")
                
                # Call the download function
                success = download_video(
                    url=url,
                    output_folder=output_folder,
                    cookie_file=cookie_file,
                    status_callback=update_status,
                    optimize_mode=optimize_mode
                )
                
                if success:
                    update_status(f"✅ Hoàn tất tải video {line_number}!", "green")
                else:
                    update_status(f"❌ Lỗi tải video {line_number}.", "red")
                    
            except Exception as e:
                update_status(f"❌ Lỗi không xác định: {str(e)}", "red")
            finally:
                self.active_downloads -= 1
                if self.active_downloads <= 0:
                    self.app.download_tab.video_download_button.config(state="normal")
                    self.app.download_tab.video_progress.stop_progress()
                    self.app.download_tab.video_progress.clear_progress()
        
        # Start download thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def get_active_downloads(self):
        """Get number of active downloads"""
        return self.active_downloads
