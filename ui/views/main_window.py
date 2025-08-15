# ui/views/main_window.py
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from ui.views.download_tab import DownloadTab
    from ui.controllers.download_controller import DownloadController
    from ui.controllers.onedrive_controller import OneDriveController
    from ui.controllers.cookie_controller import CookieController
    from core.downloader import check_ffmpeg_available
except ImportError:
    # Fallback for when running as script
    ui_dir = os.path.join(project_root, 'ui')
    core_dir = os.path.join(project_root, 'core')
    if ui_dir not in sys.path:
        sys.path.insert(0, ui_dir)
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)
    try:
        from views.download_tab import DownloadTab
        from controllers.download_controller import DownloadController
        from controllers.onedrive_controller import OneDriveController
        from controllers.cookie_controller import CookieController
        from downloader import check_ffmpeg_available
    except ImportError:
        print("Error: Could not import required modules")
        sys.exit(1)


class VideoDownloaderApp(tk.Tk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.title("🎥 Video Downloader Tool")
        self.geometry("1280x950")
        self.resizable(False, False)
        self.configure(bg="#f4f6fb")
        
        # Initialize properties
        self.ffmpeg_available = False
        self.check_dependencies()
        
        # Initialize controllers
        self.download_controller = DownloadController(self)
        self.onedrive_controller = OneDriveController(self)
        self.cookie_controller = CookieController(self)
        
        # Create UI
        self.create_widgets()
        
        # Initialize cookies after all widgets are created
        self.cookie_controller.initialize_cookies()
    
    def check_dependencies(self):
        """Check required dependencies"""
        missing_deps = []
        
        try:
            import yt_dlp
        except ImportError:
            missing_deps.append("yt-dlp")
        
        try:
            import requests
        except ImportError:
            missing_deps.append("requests")
        
        try:
            import psutil
        except ImportError:
            missing_deps.append("psutil")
        
        if missing_deps:
            print(f"⚠️ Warning: Missing dependencies: {', '.join(missing_deps)}")
            print("💡 Run: pip install -r requirements.txt")

        # Check ffmpeg availability
        try:
            self.ffmpeg_available = check_ffmpeg_available()
        except Exception:
            self.ffmpeg_available = False

    def create_widgets(self):
        """Create main application widgets"""
        # --- Header ---
        header = tk.Frame(self, bg="#3b5998", height=100)
        header.pack(fill="x")
        
        icon_label = tk.Label(header, text="🎥", font=("Segoe UI Emoji", 32), 
                            bg="#3b5998", fg="white")
        icon_label.pack(side="left", padx=(30, 10), pady=10)
        
        title_label = tk.Label(header, text="Video Downloader Tool", 
                             font=("Segoe UI", 22, "bold"), bg="#3b5998", fg="white")
        title_label.pack(side="left", pady=10)

        # --- Main content frame with tabs ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=(0, 0))
        
        # --- Download Tab ---
        self.download_tab = DownloadTab(self.notebook, self)
        self.notebook.add(self.download_tab, text="📥 Tải Video")
        
        # --- Footer ---
        footer = tk.Frame(self, bg="#e3e6f0", height=36)
        footer.pack(fill="x", side="bottom")
        
        about = tk.Label(footer, text="Make by @ HulkBeoti | 2025", 
                       font=("Segoe UI", 9), bg="#e3e6f0", fg="#888")
        about.pack(pady=8)
