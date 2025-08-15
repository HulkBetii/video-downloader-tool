# ui/views/download_tab.py
import tkinter as tk
import os
import sys

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from ui.components.url_input import URLInput
    from ui.components.cookie_input import CookieInput
    from ui.components.optimization_selector import OptimizationSelector
    from ui.components.progress_display import ProgressDisplay
except ImportError:
    # Fallback for when running as script
    ui_dir = os.path.join(project_root, 'ui')
    if ui_dir not in sys.path:
        sys.path.insert(0, ui_dir)
    try:
        from components.url_input import URLInput
        from components.cookie_input import CookieInput
        from components.optimization_selector import OptimizationSelector
        from components.progress_display import ProgressDisplay
    except ImportError:
        print("Error: Could not import required modules")
        sys.exit(1)


class DownloadTab(tk.Frame):
    """Download tab view with video and OneDrive download sections"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg="#f4f6fb")
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        """Create download tab widgets"""
        # --- Common Settings Section (Top) ---
        common_frame = tk.Frame(self, bg="#f4f6fb", relief="groove", bd=2)
        common_frame.pack(padx=20, pady=(20, 10), fill="x")
        
        # Common Settings Title
        tk.Label(common_frame, text="⚙️ Cài đặt chung", font=("Segoe UI", 12, "bold"), 
                bg="#f4f6fb", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Output Folder (Common for both)
        tk.Label(common_frame, text="💾 Thư mục lưu:", font=("Segoe UI", 11, "bold"), 
                bg="#f4f6fb").pack(anchor="w", padx=20, pady=(5, 0))
        
        path_frame = tk.Frame(common_frame, bg="#f4f6fb")
        path_frame.pack(padx=20, fill="x", pady=(5, 15))
        
        self.output_entry = tk.Entry(path_frame, font=("Segoe UI", 11), relief="groove", bd=2)
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Set default save folder
        try:
            default_download_dir = r"C:\\Users\\HH\\Downloads"
            if os.path.isdir(default_download_dir):
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, default_download_dir)
        except Exception:
            pass
        
        choose_btn = tk.Button(path_frame, text="Chọn...", command=self.select_output_folder, 
                             font=("Segoe UI", 10, "bold"), bg="#3b5998", fg="white", 
                             activebackground="#5b7bd5", activeforeground="white", 
                             relief="flat", bd=0)
        choose_btn.pack(side="left", padx=8)

        # --- Two Column Layout ---
        columns_frame = tk.Frame(self, bg="#f4f6fb")
        columns_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # --- Left Column: Video Download ---
        left_column = tk.Frame(columns_frame, bg="#f4f6fb", relief="groove", bd=2)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Video Download Title
        tk.Label(left_column, text="🎥 Tải Video", font=("Segoe UI", 12, "bold"), 
                bg="#f4f6fb", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Video URL Input
        self.video_url_input = URLInput(left_column, label_text="🔗 Video URL:")
        self.video_url_input.pack(padx=20, fill="x", pady=(0, 10))
        
        # Video Optimization Selector
        self.video_optimization = OptimizationSelector(left_column, 
                                                      ffmpeg_available=self.app.ffmpeg_available)
        self.video_optimization.pack(padx=20, fill="x", pady=(0, 10))
        
        # Video Cookie Input
        default_cookie_path = r"C:\Users\HH\Downloads\video_downloader_tool_donev1\video_downloader_tool\moithuvemmo-my.sharepoint.com_cookies.txt"
        self.video_cookie_input = CookieInput(left_column, 
                                            label_text="Dùng cookie file (.txt/.json)",
                                            default_path=default_cookie_path,
                                            button_color="#3b5998")
        self.video_cookie_input.pack(padx=20, fill="x", pady=(0, 10))
        
        # Video Progress Display
        self.video_progress = ProgressDisplay(left_column)
        self.video_progress.pack(padx=20, fill="x", pady=(0, 10))
        
        # Video Download Button
        self.video_download_button = tk.Button(left_column, text="🎥 Tải Video", 
                                             command=self.app.download_controller.start_download, 
                                             font=("Segoe UI", 12, "bold"), bg="#28a745", fg="white", 
                                             activebackground="#218838", activeforeground="white", 
                                             relief="flat", bd=0, height=2)
        self.video_download_button.pack(pady=15, ipadx=10, ipady=2)
        
        # --- Right Column: OneDrive File Download ---
        right_column = tk.Frame(columns_frame, bg="#f4f6fb", relief="groove", bd=2)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # OneDrive Title
        tk.Label(right_column, text="📁 Tải File OneDrive/SharePoint", font=("Segoe UI", 12, "bold"), 
                bg="#f4f6fb", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Hướng dẫn sử dụng
        help_text = "💡 Hỗ trợ: .rar, .zip, .pdf, .docx, .xlsx, .mp3, .mp4 và nhiều định dạng khác"
        help_text2 = "🌐 Hỗ trợ: OneDrive, SharePoint, Office 365"
        tk.Label(right_column, text=help_text, font=("Segoe UI", 9), bg="#f4f6fb", 
                fg="#7f8c8d").pack(anchor="w", padx=20, pady=(0, 5))
        tk.Label(right_column, text=help_text2, font=("Segoe UI", 9), bg="#f4f6fb", 
                fg="#7f8c8d").pack(anchor="w", padx=20, pady=(0, 10))
        
        # OneDrive URL Input
        self.onedrive_url_input = URLInput(right_column, label_text="🔗 OneDrive/SharePoint URL:")
        self.onedrive_url_input.pack(padx=20, fill="x", pady=(0, 10))
        
        # OneDrive Cookie Input
        default_onedrive_cookie_path = r"C:\Users\HH\Downloads\video_downloader_tool_donev1\video_downloader_tool\moithuvemmo-my.sharepoint.com_cookies.txt"
        self.onedrive_cookie_input = CookieInput(right_column, 
                                               label_text="Dùng cookie file cho OneDrive",
                                               default_path=default_onedrive_cookie_path,
                                               button_color="#e67e22")
        self.onedrive_cookie_input.pack(padx=20, fill="x", pady=(0, 10))
        
        # OneDrive Progress Display
        self.onedrive_progress = ProgressDisplay(right_column)
        self.onedrive_progress.pack(padx=20, fill="x", pady=(0, 10))
        
        # OneDrive Download Button
        self.onedrive_download_button = tk.Button(right_column, text="📁 Tải File OneDrive/SharePoint", 
                                                command=self.app.onedrive_controller.start_onedrive_download, 
                                                font=("Segoe UI", 12, "bold"), bg="#e67e22", fg="white", 
                                                activebackground="#d35400", activeforeground="white", 
                                                relief="flat", bd=0, height=2)
        self.onedrive_download_button.pack(pady=15, ipadx=10, ipady=2)
    
    def select_output_folder(self):
        """Open folder dialog to select output directory"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title="Chọn thư mục lưu")
        if folder_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder_path)
