# ui/downloader_ui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import sys
import platform

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.downloader import download_video
    from utils.system_optimizer import SystemOptimizer
except ImportError:
    # Fallback for when running as script
    core_dir = os.path.join(project_root, 'core')
    utils_dir = os.path.join(project_root, 'utils')
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    try:
        from downloader import download_video
        from system_optimizer import SystemOptimizer
    except ImportError:
        print("Error: Could not import required modules")
        print("Make sure you're running from the video_downloader_tool directory")
        sys.exit(1)


class VideoDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎥 Video Downloader Tool")
        self.geometry("1280x990")
        self.resizable(False, False)
        self.configure(bg="#f4f6fb")
        self.active_downloads = 0  # Đếm số video đang tải
        self.active_onedrive_downloads = 0  # Đếm số file OneDrive đang tải
        self.check_dependencies()
        self.create_widgets()
    
    def check_dependencies(self):
        """Kiểm tra các dependencies cần thiết"""
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

    def create_widgets(self):
        # --- Header ---
        header = tk.Frame(self, bg="#3b5998", height=100)
        header.pack(fill="x")
        icon_label = tk.Label(header, text="🎥", font=("Segoe UI Emoji", 32), bg="#3b5998", fg="white")
        icon_label.pack(side="left", padx=(30, 10), pady=10)
        title_label = tk.Label(header, text="Video Downloader Tool", font=("Segoe UI", 22, "bold"), bg="#3b5998", fg="white")
        title_label.pack(side="left", pady=10)

        # --- Main content frame with tabs ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=(0, 0))
        
        # --- Download Tab ---
        self.download_tab = tk.Frame(self.notebook, bg="#f4f6fb")
        self.notebook.add(self.download_tab, text="📥 Tải Video")
        
        # --- Optimization Tab ---
        self.optimization_tab = tk.Frame(self.notebook, bg="#f4f6fb")
        self.notebook.add(self.optimization_tab, text="⚡ Tối ưu hóa")
        
        # Create download tab content
        self.create_download_tab()
        
        # Create optimization tab content
        self.create_optimization_tab()
        
        # --- Footer ---
        footer = tk.Frame(self, bg="#e3e6f0", height=36)
        footer.pack(fill="x", side="bottom")
        about = tk.Label(footer, text="Make by @ HulkBeoti | 2025", font=("Segoe UI", 9), bg="#e3e6f0", fg="#888")
        about.pack(pady=8)

    def create_download_tab(self):
        """Tạo nội dung cho tab Download với layout 2 cột"""
        main_frame = self.download_tab
        
        # --- Common Settings Section (Top) ---
        common_frame = tk.Frame(main_frame, bg="#f4f6fb", relief="groove", bd=2)
        common_frame.pack(padx=20, pady=(20, 10), fill="x")
        
        # Common Settings Title
        tk.Label(common_frame, text="⚙️ Cài đặt chung", font=("Segoe UI", 12, "bold"), bg="#f4f6fb", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Output Folder (Common for both)
        tk.Label(common_frame, text="💾 Thư mục lưu:", font=("Segoe UI", 11, "bold"), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(5, 0))
        path_frame = tk.Frame(common_frame, bg="#f4f6fb")
        path_frame.pack(padx=20, fill="x", pady=(5, 15))
        self.output_entry = tk.Entry(path_frame, font=("Segoe UI", 11), relief="groove", bd=2)
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=5)
        choose_btn = tk.Button(path_frame, text="Chọn...", command=self.select_output_folder, font=("Segoe UI", 10, "bold"), bg="#3b5998", fg="white", activebackground="#5b7bd5", activeforeground="white", relief="flat", bd=0)
        choose_btn.pack(side="left", padx=8)

        # --- Two Column Layout ---
        columns_frame = tk.Frame(main_frame, bg="#f4f6fb")
        columns_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # --- Left Column: Video Download ---
        left_column = tk.Frame(columns_frame, bg="#f4f6fb", relief="groove", bd=2)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Video Download Title
        tk.Label(left_column, text="🎥 Tải Video", font=("Segoe UI", 12, "bold"), bg="#f4f6fb", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Video URL Input
        url_frame = tk.Frame(left_column, bg="#f4f6fb")
        url_frame.pack(padx=20, fill="x", pady=(0, 10))
        tk.Label(url_frame, text="🔗 Video URL:", font=("Segoe UI", 11, "bold"), bg="#f4f6fb").pack(anchor="w")
        self.url_entry = tk.Text(url_frame, width=40, height=3, font=("Segoe UI", 11), relief="groove", bd=2)
        self.url_entry.pack(fill="x", pady=(5, 0), ipady=5)

        # Optimization Mode
        tk.Label(left_column, text="⚡ Chế độ tối ưu hóa:", font=("Segoe UI", 11, "bold"), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(10, 0))
        self.optimize_mode = tk.StringVar(value="balanced")
        optimize_frame = tk.Frame(left_column, bg="#f4f6fb")
        optimize_frame.pack(padx=20, fill="x", pady=(0, 10))
        style = {"font": ("Segoe UI", 9), "bg": "#f4f6fb"}
        tk.Radiobutton(optimize_frame, text="Cân bằng", variable=self.optimize_mode, value="balanced", selectcolor="#e3e6f0", **style).pack(anchor="w", pady=2)
        tk.Radiobutton(optimize_frame, text="Tốc độ cao", variable=self.optimize_mode, value="speed", selectcolor="#e3e6f0", **style).pack(anchor="w", pady=2)
        tk.Radiobutton(optimize_frame, text="Chất lượng cao", variable=self.optimize_mode, value="quality", selectcolor="#e3e6f0", **style).pack(anchor="w", pady=2)
        tk.Radiobutton(optimize_frame, text="🚀 Tốc độ + Chất lượng", variable=self.optimize_mode, value="speed_quality", selectcolor="#e3e6f0", **style).pack(anchor="w", pady=2)

        # Video Cookie file
        self.use_cookies = tk.BooleanVar()
        tk.Checkbutton(left_column, text="Dùng cookie file (.txt/.json)", variable=self.use_cookies, command=self.toggle_cookie_entry, font=("Segoe UI", 10), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(5, 0))
        cookie_frame = tk.Frame(left_column, bg="#f4f6fb")
        cookie_frame.pack(padx=20, fill="x", pady=(5, 10))
        self.cookie_entry = tk.Entry(cookie_frame, state="disabled", font=("Segoe UI", 10), relief="groove", bd=2)
        self.cookie_entry.pack(side="left", fill="x", expand=True, ipady=4)
        cookie_btn = tk.Button(cookie_frame, text="Chọn...", command=self.select_cookie_file, font=("Segoe UI", 10, "bold"), bg="#3b5998", fg="white", activebackground="#5b7bd5", activeforeground="white", relief="flat", bd=0)
        cookie_btn.pack(side="left", padx=8)

        # Video Progress Bar
        self.progress_frame = tk.Frame(left_column, bg="#f4f6fb")
        self.progress_frame.pack(padx=20, pady=(10, 0), fill="x")
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x")

        # Video Download Button
        self.download_button = tk.Button(left_column, text="🎥 Tải Video", command=self.start_download, font=("Segoe UI", 12, "bold"), bg="#28a745", fg="white", activebackground="#218838", activeforeground="white", relief="flat", bd=0, height=2)
        self.download_button.pack(pady=15, ipadx=10, ipady=2)
        
        # Video Status
        self.status_label = tk.Label(left_column, text="Sẵn sàng tải video.", fg="#3b5998", bg="#f4f6fb", font=("Segoe UI", 10, "italic"), wraplength=250)
        self.status_label.pack(pady=5)
        
        # --- Right Column: OneDrive File Download ---
        right_column = tk.Frame(columns_frame, bg="#f4f6fb", relief="groove", bd=2)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # OneDrive Title
        tk.Label(right_column, text="📁 Tải File OneDrive/SharePoint", font=("Segoe UI", 12, "bold"), bg="#f4f6fb", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Hướng dẫn sử dụng
        help_text = "💡 Hỗ trợ: .rar, .zip, .pdf, .docx, .xlsx, .mp3, .mp4 và nhiều định dạng khác"
        help_text2 = "🌐 Hỗ trợ: OneDrive, SharePoint, Office 365"
        tk.Label(right_column, text=help_text, font=("Segoe UI", 9), bg="#f4f6fb", fg="#7f8c8d").pack(anchor="w", padx=20, pady=(0, 5))
        tk.Label(right_column, text=help_text2, font=("Segoe UI", 9), bg="#f4f6fb", fg="#7f8c8d").pack(anchor="w", padx=20, pady=(0, 10))
        
        # OneDrive URL Input
        onedrive_url_frame = tk.Frame(right_column, bg="#f4f6fb")
        onedrive_url_frame.pack(padx=20, fill="x", pady=(0, 10))
        tk.Label(onedrive_url_frame, text="🔗 OneDrive/SharePoint URL:", font=("Segoe UI", 11, "bold"), bg="#f4f6fb").pack(anchor="w")
        self.onedrive_url_entry = tk.Entry(onedrive_url_frame, font=("Segoe UI", 11), relief="groove", bd=2)
        self.onedrive_url_entry.pack(fill="x", pady=(5, 0), ipady=5)
        
        # OneDrive Cookie file
        self.onedrive_use_cookies = tk.BooleanVar()
        tk.Checkbutton(right_column, text="Dùng cookie file cho OneDrive", variable=self.onedrive_use_cookies, command=self.toggle_onedrive_cookie_entry, font=("Segoe UI", 10), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(10, 0))
        onedrive_cookie_frame = tk.Frame(right_column, bg="#f4f6fb")
        onedrive_cookie_frame.pack(padx=20, fill="x", pady=(5, 10))
        self.onedrive_cookie_entry = tk.Entry(onedrive_cookie_frame, state="disabled", font=("Segoe UI", 10), relief="groove", bd=2)
        self.onedrive_cookie_entry.pack(side="left", fill="x", expand=True, ipady=4)
        onedrive_cookie_btn = tk.Button(onedrive_cookie_frame, text="Chọn...", command=self.select_onedrive_cookie_file, font=("Segoe UI", 10, "bold"), bg="#e67e22", fg="white", activebackground="#d35400", activeforeground="white", relief="flat", bd=0)
        onedrive_cookie_btn.pack(side="left", padx=8)
        
        # OneDrive Progress Bar
        self.onedrive_progress_frame = tk.Frame(right_column, bg="#f4f6fb")
        self.onedrive_progress_frame.pack(padx=20, pady=(10, 0), fill="x")
        self.onedrive_progress_bar = ttk.Progressbar(self.onedrive_progress_frame, mode='indeterminate')
        self.onedrive_progress_bar.pack(fill="x")
        
        # OneDrive Download Button
        self.onedrive_download_button = tk.Button(right_column, text="📁 Tải File OneDrive/SharePoint", command=self.start_onedrive_download, font=("Segoe UI", 12, "bold"), bg="#e67e22", fg="white", activebackground="#d35400", activeforeground="white", relief="flat", bd=0, height=2)
        self.onedrive_download_button.pack(pady=15, ipadx=10, ipady=2)
        
        # OneDrive Status
        self.onedrive_status_label = tk.Label(right_column, text="Sẵn sàng tải file từ OneDrive/SharePoint.", fg="#e67e22", bg="#f4f6fb", font=("Segoe UI", 10, "italic"), wraplength=250)
        self.onedrive_status_label.pack(pady=5)

    def create_optimization_tab(self):
        """Tạo nội dung cho tab Tối ưu hóa"""
        main_frame = self.optimization_tab
        
        # Initialize system optimizer
        try:
            self.system_optimizer = SystemOptimizer()
        except Exception as e:
            self.system_optimizer = None
            print(f"Warning: Could not initialize SystemOptimizer: {e}")
        
        # --- System Info Section ---
        info_frame = tk.Frame(main_frame, bg="#f4f6fb", relief="groove", bd=2)
        info_frame.pack(padx=40, pady=(30, 20), fill="x")
        
        tk.Label(info_frame, text="🖥️ Thông tin hệ thống", font=("Segoe UI", 12, "bold"), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(15, 10))
        
        if self.system_optimizer:
            # System specs
            specs_frame = tk.Frame(info_frame, bg="#f4f6fb")
            specs_frame.pack(padx=20, fill="x", pady=(0, 15))
            
            specs_text = f"💻 CPU: {self.system_optimizer.cpu_count} cores\n"
            specs_text += f"💾 RAM: {self.system_optimizer.memory_gb:.1f} GB\n"
            specs_text += f"🖥️  OS: {platform.system()} {platform.release()}"
            
            tk.Label(specs_frame, text=specs_text, font=("Segoe UI", 10), bg="#f4f6fb", justify="left").pack(anchor="w")
        else:
            tk.Label(info_frame, text="⚠️ Không thể lấy thông tin hệ thống", font=("Segoe UI", 10), bg="#f4f6fb", fg="orange").pack(padx=20, pady=(0, 15))
        
        # --- Performance Report Section ---
        perf_frame = tk.Frame(main_frame, bg="#f4f6fb", relief="groove", bd=2)
        perf_frame.pack(padx=40, pady=(0, 20), fill="x")
        
        tk.Label(perf_frame, text="📊 Báo cáo hiệu suất", font=("Segoe UI", 12, "bold"), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(15, 10))
        
        self.perf_text = tk.Text(perf_frame, height=8, font=("Consolas", 9), bg="#f8f9fa", relief="sunken", bd=1)
        self.perf_text.pack(padx=20, pady=(0, 15), fill="x")
        
        # Refresh button
        refresh_btn = tk.Button(perf_frame, text="🔄 Làm mới", command=self.refresh_performance, font=("Segoe UI", 10, "bold"), bg="#17a2b8", fg="white", activebackground="#138496", activeforeground="white", relief="flat", bd=0)
        refresh_btn.pack(pady=(0, 15))
        
        # --- Optimization Tips Section ---
        tips_frame = tk.Frame(main_frame, bg="#f4f6fb", relief="groove", bd=2)
        tips_frame.pack(padx=40, pady=(0, 20), fill="x")
        
        tk.Label(tips_frame, text="💡 Mẹo tối ưu hóa", font=("Segoe UI", 12, "bold"), bg="#f4f6fb").pack(anchor="w", padx=20, pady=(15, 10))
        
        self.tips_text = tk.Text(tips_frame, height=10, font=("Segoe UI", 9), bg="#f8f9fa", relief="sunken", bd=1, wrap="word")
        self.tips_text.pack(padx=20, pady=(0, 15), fill="x")
        
        # Load initial data
        self.refresh_performance()
        self.load_optimization_tips()

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)

    def select_cookie_file(self):
        file = filedialog.askopenfilename(
            filetypes=[
                ("Cookie files", "*.txt;*.json"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if file:
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, file)

    def select_onedrive_cookie_file(self):
        file = filedialog.askopenfilename(
            filetypes=[
                ("Cookie files", "*.txt;*.json"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if file:
            self.onedrive_cookie_entry.delete(0, tk.END)
            self.onedrive_cookie_entry.insert(0, file)

    def toggle_onedrive_cookie_entry(self):
        state = "normal" if self.onedrive_use_cookies.get() else "disabled"
        self.onedrive_cookie_entry.config(state=state)

    def toggle_cookie_entry(self):
        state = "normal" if self.use_cookies.get() else "disabled"
        self.cookie_entry.config(state=state)

    def start_download(self):
        url_text = self.url_entry.get("1.0", tk.END)
        urls = [u.strip() for u in url_text.splitlines() if u.strip()]
        output_folder = self.output_entry.get().strip()
        cookie_file = self.cookie_entry.get().strip() if self.use_cookies.get() else None
        optimize_mode = self.optimize_mode.get()

        if not urls or not output_folder:
            messagebox.showerror("Thiếu thông tin", "Vui lòng nhập URL và chọn thư mục lưu.")
            return

        self.download_button.config(state="disabled")
        self.progress_bar.start()
        self.status_label.config(text=f"⏳ Đang tải {len(urls)} video...", fg="#ff9800")
        self.active_downloads = len(urls)
        for url in urls:
            threading.Thread(target=self.run_download, args=(url, output_folder, cookie_file, optimize_mode)).start()

    def run_download(self, url, output_folder, cookie_file, optimize_mode):
        def update_status(status_text, color="#3b5998"):
            self.status_label.config(text=status_text, fg=color)

        try:
            download_video(url, output_folder, cookie_file, status_callback=update_status, optimize_mode=optimize_mode)
        except Exception as e:
            update_status(f"❌ Lỗi: {e}", "red")
        finally:
            self.active_downloads -= 1
            if self.active_downloads <= 0:
                self.progress_bar.stop()
                self.download_button.config(state="normal")
                self.status_label.config(text="✅ Đã tải xong tất cả video!", fg="#28a745")
            else:
                self.status_label.config(text=f"⏳ Đang tải {self.active_downloads} video còn lại...", fg="#ff9800")

    def start_onedrive_download(self):
        """Bắt đầu tải file từ OneDrive/SharePoint"""
        onedrive_url = self.onedrive_url_entry.get().strip()
        output_folder = self.output_entry.get().strip()
        cookie_file = self.onedrive_cookie_entry.get().strip() if self.onedrive_use_cookies.get() else None

        if not onedrive_url or not output_folder:
            messagebox.showerror("Thiếu thông tin", "Vui lòng nhập OneDrive/SharePoint URL và chọn thư mục lưu.")
            return

        # Kiểm tra URL OneDrive/SharePoint
        if not self.is_onedrive_url(onedrive_url):
            messagebox.showerror("URL không hợp lệ", "Vui lòng nhập URL OneDrive/SharePoint hợp lệ (ví dụ: https://1drv.ms/v/s!... hoặc https://yourdomain.sharepoint.com/...)")
            return

        self.onedrive_download_button.config(state="disabled")
        self.onedrive_progress_bar.start()
        self.onedrive_status_label.config(text="⏳ Đang tải file từ OneDrive/SharePoint...", fg="#e67e22")
        self.active_onedrive_downloads += 1
        
        # Chạy tải file trong thread riêng
        threading.Thread(target=self.run_onedrive_download, args=(onedrive_url, output_folder, cookie_file)).start()

    def run_onedrive_download(self, onedrive_url, output_folder, cookie_file):
        """Chạy tải file OneDrive/SharePoint trong thread riêng"""
        def update_status(status_text, color="#e67e22"):
            self.onedrive_status_label.config(text=status_text, fg=color)

        try:
            # Sử dụng yt-dlp để tải file từ OneDrive/SharePoint
            self.download_onedrive_file(onedrive_url, output_folder, cookie_file, update_status)
        except Exception as e:
            update_status(f"❌ Lỗi: {e}", "red")
        finally:
            self.active_onedrive_downloads -= 1
            if self.active_onedrive_downloads <= 0:
                self.onedrive_progress_bar.stop()
                self.onedrive_download_button.config(state="normal")
                self.onedrive_status_label.config(text="✅ Đã tải xong tất cả file!", fg="#27ae60")
            else:
                self.onedrive_status_label.config(text=f"⏳ Đang tải {self.active_onedrive_downloads} file còn lại...", fg="#e67e22")

    def download_onedrive_file(self, onedrive_url, output_folder, cookie_file, status_callback):
        """Tải file từ OneDrive/SharePoint sử dụng yt-dlp"""
        try:
            import yt_dlp
            
            # Debug: Kiểm tra URL
            status_callback(f"🔍 Đang kiểm tra URL: {onedrive_url[:100]}...", "blue")
            
            # Kiểm tra nếu là SharePoint URL phức tạp
            if self.is_complex_sharepoint_url(onedrive_url):
                status_callback("🔍 Phát hiện SharePoint URL phức tạp, đang xử lý...", "blue")
                return self.handle_complex_sharepoint(onedrive_url, output_folder, cookie_file, status_callback)
            else:
                status_callback("🔍 Không phải SharePoint URL phức tạp, sử dụng yt-dlp...", "blue")
            
            # Cấu hình yt-dlp cho OneDrive/SharePoint
            ydl_opts = {
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'quiet': False,
                'noplaylist': True,
                'restrictfilenames': False,
                'concurrent_fragment_downloads': 8,
                'buffersize': 2048,
                'http_chunk_size': 10485760,  # 10MB chunks
                'retries': 5,  # Tăng retry cho SharePoint
                'fragment_retries': 5,
                'socket_timeout': 60,  # Tăng timeout cho SharePoint
                'ignoreerrors': False,
                'no_warnings': False,
                'extractor_retries': 5,  # Tăng retry cho extractor
                'fragment_retries': 5,
                'skip_unavailable_fragments': True,
            }

            # Thêm cookies nếu có
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file
                status_callback("🍪 Sử dụng cookies cho OneDrive/SharePoint", "blue")
                
                # Kiểm tra cookies có hợp lệ không
                try:
                    from utils.cookies import is_valid_cookie_file
                    if is_valid_cookie_file(cookie_file):
                        status_callback("✅ Cookies hợp lệ", "green")
                    else:
                        status_callback("⚠️ Cookies có thể không hợp lệ", "orange")
                except ImportError:
                    status_callback("🍪 Cookies đã được thêm", "blue")
            
            # Xử lý đặc biệt cho SharePoint URLs
            if 'sharepoint.com' in onedrive_url.lower():
                status_callback("🔍 Phát hiện SharePoint URL, đang xử lý...", "blue")
                
                # Xử lý đặc biệt cho SharePoint sharing URLs (:u:/r/)
                if ':u:/r/' in onedrive_url:
                    status_callback("🔍 Phát hiện SharePoint sharing URL, đang xử lý...", "blue")
                    # Thử chuyển đổi URL sharing thành URL download
                    converted_url = self.convert_sharepoint_sharing_url(onedrive_url)
                    if converted_url:
                        status_callback(f"🔄 Đã chuyển đổi URL: {converted_url[:100]}...", "blue")
                        onedrive_url = converted_url
                
                # Thêm headers đặc biệt cho SharePoint
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://moithuvemmo-my.sharepoint.com/',
                }
                # Tăng timeout cho SharePoint
                ydl_opts['socket_timeout'] = 120
                ydl_opts['extractor_retries'] = 10
                
                # Thêm extractor args đặc biệt cho SharePoint
                ydl_opts['extractor_args'] = {
                    'generic': {
                        'extract_flat': False,
                        'no_warnings': False,
                    }
                }

            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '').strip()
                    speed = d.get('_speed_str', '').strip()
                    eta = d.get('eta_str', '').strip()
                    if status_callback:
                        status_text = f"📥 Đang tải: {percent} | Tốc độ: {speed}"
                        if eta:
                            status_text += f" | Còn lại: {eta}"
                        status_callback(status_text, "blue")
                elif d['status'] == 'finished':
                    if status_callback:
                        status_callback("✅ Hoàn tất tải file!", "green")

            ydl_opts['progress_hooks'] = [progress_hook]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_callback("🔍 Đang phân tích URL OneDrive...", "blue")
                ydl.download([onedrive_url])

        except ImportError:
            status_callback("❌ Lỗi: yt-dlp không được cài đặt", "red")
        except Exception as e:
            status_callback(f"❌ Lỗi khi tải file: {str(e)}", "red")

    def is_onedrive_url(self, url):
        """Kiểm tra xem URL có phải là OneDrive/SharePoint không"""
        onedrive_domains = [
            '1drv.ms',
            'onedrive.live.com',
            'sharepoint.com',
            'office.com',
            'moithuvemmo-my.sharepoint.com'  # Custom SharePoint domain
        ]
        return any(domain in url.lower() for domain in onedrive_domains)
    
    def is_complex_sharepoint_url(self, url):
        """Kiểm tra xem có phải SharePoint URL phức tạp không"""
        url_lower = url.lower()
        
        # Debug logging
        print(f"🔍 Debug: Kiểm tra URL: {url[:100]}...")
        print(f"🔍 Debug: sharepoint.com in URL: {'sharepoint.com' in url_lower}")
        print(f"🔍 Debug: :u:/r/ in URL: {':u:/r/' in url}")
        print(f"🔍 Debug: _layouts/15/onedrive.aspx in URL: {'_layouts/15/onedrive.aspx' in url_lower}")
        print(f"🔍 Debug: id= in URL: {'id=' in url_lower}")
        print(f"🔍 Debug: parent= in URL: {'parent=' in url_lower}")
        print(f"🔍 Debug: URL length: {len(url)}")
        
        is_complex = ('sharepoint.com' in url_lower and 
                (':u:/r/' in url or  # SharePoint sharing URL format
                 '_layouts/15/onedrive.aspx' in url_lower or 
                 'id=' in url_lower or 
                 'parent=' in url_lower or
                 len(url) > 200))  # Giảm ngưỡng để bắt nhiều URL hơn
        
        print(f"🔍 Debug: Is complex SharePoint URL: {is_complex}")
        return is_complex
    
    def handle_complex_sharepoint(self, url, output_folder, cookie_file, status_callback):
        """
        Enhanced SharePoint download handler with proper URL parsing
        """
        try:
            import requests
            import urllib.parse
            import os
            import re
            
            status_callback("🔄 Enhanced SharePoint download starting...", "blue")
            
            # Step 1: Extract filename properly
            filename = self.extract_filename_from_url(url)
            status_callback(f"📁 Detected filename: {filename}", "green")
            
            # Step 2: Create session with proper headers
            session = requests.Session()
            
            # Load cookies if available
            if cookie_file and os.path.exists(cookie_file):
                try:
                    from utils.cookies import load_cookies_from_file
                    cookies = load_cookies_from_file(cookie_file)
                    if cookies:
                        session.cookies.update(cookies)
                        status_callback(f"🍪 Loaded {len(cookies)} cookies", "green")
                        
                        # Add SharePoint-specific cookies if missing
                        sharepoint_cookies = {
                            'SPOIDCRL': '1',  # SharePoint Online IDCRL
                            'WSS_FullScreenMode': 'false',
                            'SPRequestGuid': '1',
                            'SPOIDCRL': '1'
                        }
                        
                        # Only add if not already present
                        for name, value in sharepoint_cookies.items():
                            if name not in session.cookies:
                                session.cookies.set(name, value, domain='.sharepoint.com')
                        
                        print(f"🔍 Debug: Enhanced with SharePoint cookies")
                        
                except Exception as e:
                    status_callback(f"Warning: Cookie loading failed: {e}", "orange")
            
            # Step 3: Try multiple download approaches
            download_success = False
            
            # Approach 1: Convert sharing URL to direct download URL
            status_callback("🔄 Trying direct URL conversion...", "blue")
            direct_urls = self.create_multiple_download_urls(url)
            
            for i, direct_url in enumerate(direct_urls):
                if direct_url:
                    status_callback(f"🔗 Trying download URL #{i+1}...", "blue")
                    print(f"🔍 Debug: Attempting URL: {direct_url[:100]}...")
                    
                    if self.download_from_url(direct_url, output_folder, filename, session, status_callback):
                        download_success = True
                        break
            
            # Approach 2: Parse SharePoint page for download links
            if not download_success:
                status_callback("🔄 Trying page parsing method...", "blue")
                download_links = self.extract_download_links_from_page(url, session, status_callback)
                
                for link in download_links:
                    if self.download_from_url(link, output_folder, filename, session, status_callback):
                        download_success = True
                        break
            
            # Approach 3: Use yt-dlp as final fallback
            if not download_success:
                status_callback("🔄 Trying yt-dlp fallback...", "blue")
                download_success = self.ytdlp_sharepoint_download(url, output_folder, filename, cookie_file, status_callback)
            
            if download_success:
                status_callback(f"✅ Successfully downloaded: {filename}", "green")
            else:
                status_callback("❌ All download methods failed", "red")
                self.provide_manual_download_guidance(url, status_callback)
            
            return download_success
            
        except Exception as e:
            status_callback(f"❌ SharePoint download error: {str(e)}", "red")
            return False
    
    def get_sharepoint_direct_url(self, sharing_url, status_callback):
        """
        Convert SharePoint sharing URL to direct download URL
        Try multiple approaches
        """
        try:
            print(f"🔍 Debug: get_sharepoint_direct_url - input: {sharing_url[:100]}...")
            
            # Approach 1: SharePoint API
            api_url = self.create_sharepoint_api_url(sharing_url)
            if api_url:
                status_callback("🔗 Created SharePoint API URL", "green")
                return api_url
            
            # Approach 2: Direct file access
            direct_url = self.create_direct_file_url(sharing_url)
            if direct_url:
                status_callback("🔗 Created direct file URL", "green")
                return direct_url
                
            # Approach 3: Download parameter modification
            download_url = self.modify_url_for_download(sharing_url)
            if download_url:
                status_callback("🔗 Modified URL for download", "green")
                return download_url
            
            # Approach 4: Try to create a simple direct download URL
            simple_url = self.create_simple_download_url(sharing_url)
            if simple_url:
                status_callback("🔗 Created simple download URL", "green")
                return simple_url
            
            # Approach 5: Try direct file access without download parameter
            direct_url = self.create_direct_file_url(sharing_url)
            if direct_url:
                status_callback("🔗 Created direct file access URL", "green")
                return direct_url
            
            # Approach 6: Try SharePoint download.aspx format
            download_aspx_url = self.create_sharepoint_download_aspx_url(sharing_url)
            if download_aspx_url:
                status_callback("🔗 Created SharePoint download.aspx URL", "green")
                return download_aspx_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in get_sharepoint_direct_url: {e}")
            return None
    
    def create_sharepoint_api_url(self, sharing_url):
        """Create proper SharePoint Graph API download URL"""
        try:
            import urllib.parse
            import base64
            import json
            
            print(f"🔍 Debug: create_sharepoint_api_url - input: {sharing_url[:100]}...")
            
            # Extract sharing token from URL
            if ':u:/r/' in sharing_url:
                parts = sharing_url.split(':u:/r/')
                if len(parts) == 2:
                    base_url = parts[0]
                    encoded_path = parts[1]
                    
                    # Parse domain and site info
                    domain_parts = base_url.replace('https://', '').split('/')
                    domain = domain_parts[0]
                    
                    # Create Graph API URL using sharing token approach
                    sharing_url_encoded = base64.b64encode(sharing_url.encode()).decode().rstrip('=')
                    graph_url = f"https://graph.microsoft.com/v1.0/shares/u!{sharing_url_encoded}/root/content"
                    
                    print(f"🔍 Debug: Created Graph API URL: {graph_url[:100]}...")
                    return graph_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error creating SharePoint API URL: {e}")
            return None
    
    def create_direct_file_url(self, sharing_url):
        """Create direct file access URL"""
        try:
            print(f"🔍 Debug: create_direct_file_url - input: {sharing_url[:100]}...")
            
            if ':u:/r/' in sharing_url:
                # Convert sharing URL to direct access URL
                parts = sharing_url.split(':u:/r/')
                if len(parts) == 2:
                    base_url = parts[0].rstrip('/')
                    path_part = parts[1]
                    
                    # Handle path properly - avoid duplicate 'personal/'
                    if path_part.startswith('personal/'):
                        clean_path = path_part
                    else:
                        clean_path = f"personal/{path_part}"
                    
                    # Create direct file access URL
                    direct_url = f"{base_url}/{clean_path}"
                    print(f"🔍 Debug: Created direct file URL: {direct_url[:100]}...")
                    print(f"🔍 Debug: Clean path: {clean_path}")
                    return direct_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in create_direct_file_url: {e}")
            return None
    
    def create_sharepoint_download_aspx_url(self, sharing_url):
        """Create SharePoint download.aspx URL"""
        try:
            print(f"🔍 Debug: create_sharepoint_download_aspx_url - input: {sharing_url[:100]}...")
            
            if ':u:/r/' in sharing_url:
                # Convert sharing URL to download.aspx format
                parts = sharing_url.split(':u:/r/')
                if len(parts) == 2:
                    base_url = parts[0].rstrip('/')
                    path_part = parts[1]
                    
                    # Handle path properly
                    if path_part.startswith('personal/'):
                        clean_path = path_part
                    else:
                        clean_path = f"personal/{path_part}"
                    
                    # Create SharePoint download.aspx URL
                    download_url = f"{base_url}/{clean_path}/_layouts/15/download.aspx"
                    print(f"🔍 Debug: Created download.aspx URL: {download_url[:100]}...")
                    print(f"🔍 Debug: Clean path: {clean_path}")
                    return download_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in create_sharepoint_download_aspx_url: {e}")
            return None
    
    def get_sharepoint_download_url_from_page(self, sharing_url, session, status_callback):
        """Extract download URL by parsing SharePoint page content"""
        try:
            # First, get the page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': sharing_url,
            }
            
            response = session.get(sharing_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML to find download links
            import re
            
            # Look for download.aspx links
            download_patterns = [
                r'href=["\']([^"\']*download\.aspx[^"\']*)["\']',
                r'href=["\']([^"\']*downloadRedirect[^"\']*)["\']',
                r'"downloadUrl":\s*"([^"]*)"',
                r'"@microsoft.graph.downloadUrl":\s*"([^"]*)"'
            ]
            
            for pattern in download_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        return match
                    elif match.startswith('/'):
                        from urllib.parse import urljoin
                        return urljoin(sharing_url, match)
            
            return None
        except Exception as e:
            status_callback(f"Error parsing SharePoint page: {str(e)}", "orange")
            return None
    
    def modify_url_for_download(self, sharing_url):
        """Modify URL to force download"""
        try:
            print(f"🔍 Debug: modify_url_for_download - input: {sharing_url[:100]}...")
            
            if '_layouts/15/onedrive.aspx' in sharing_url:
                # Replace with download.aspx
                download_url = sharing_url.replace('onedrive.aspx', 'download.aspx')
                print(f"🔍 Debug: Modified URL for download: {download_url[:100]}...")
                return download_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in modify_url_for_download: {e}")
            return None
    
    def create_simple_download_url(self, sharing_url):
        """Create a simple direct download URL for SharePoint"""
        try:
            print(f"🔍 Debug: create_simple_download_url - input: {sharing_url[:100]}...")
            
            if ':u:/r/' in sharing_url:
                # Convert sharing URL to simple download URL
                parts = sharing_url.split(':u:/r/')
                if len(parts) == 2:
                    base_url = parts[0].rstrip('/')
                    path_part = parts[1]
                    
                    # Remove duplicate 'personal/' if exists
                    if path_part.startswith('personal/'):
                        clean_path = path_part
                    else:
                        clean_path = f"personal/{path_part}"
                    
                    # Create simple download URL by adding download parameter
                    simple_url = f"{base_url}/{clean_path}?download=1"
                    print(f"🔍 Debug: Created simple download URL: {simple_url[:100]}...")
                    print(f"🔍 Debug: Clean path: {clean_path}")
                    return simple_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in create_simple_download_url: {e}")
            return None
    
    def extract_filename_from_url(self, url):
        """
        Enhanced filename extraction for SharePoint URLs
        Properly handles URL encoding and extracts complete filename with extension
        """
        try:
            import urllib.parse
            import re
            
            print(f"🔍 Debug: extract_filename_from_url - URL: {url[:150]}...")
            
            # Method 1: Extract from the end of the URL path (most reliable for SharePoint)
            if ':u:/r/' in url:
                # Split and get the path part
                path_part = url.split(':u:/r/')[1] if ':u:/r/' in url else url
                
                # Remove query parameters first
                if '?' in path_part:
                    path_part = path_part.split('?')[0]
                
                # URL decode the entire path
                decoded_path = urllib.parse.unquote(path_part)
                print(f"🔍 Debug: decoded_path: {decoded_path}")
                
                # Split by '/' and find the last part that contains a file extension
                path_segments = decoded_path.split('/')
                print(f"🔍 Debug: path_segments: {path_segments}")
                
                # Look for filename from the end
                for i in range(len(path_segments) - 1, -1, -1):
                    segment = path_segments[i].strip()
                    # Check if segment contains file extension
                    if re.search(r'\.(rar|zip|pdf|docx?|xlsx?|pptx?|mp[34]|avi|mkv|mov|wmv|flv|webm|m4v)$', segment, re.IGNORECASE):
                        print(f"🔍 Debug: Found filename with extension: {segment}")
                        return segment
                
                # If no extension found, take the last non-empty segment and try to determine extension
                for i in range(len(path_segments) - 1, -1, -1):
                    segment = path_segments[i].strip()
                    if segment and segment not in ['Documents', 'Shared Documents', 'personal']:
                        # Try to determine file type from context or assume common extension
                        filename = segment
                        
                        # Check if this looks like a course/lesson name, assume it's a RAR file
                        if any(keyword in filename.lower() for keyword in ['khóa học', 'course', 'lesson', 'bài', 'chương']):
                            filename += '.rar'
                        
                        print(f"🔍 Debug: Filename without extension, assumed: {filename}")
                        return filename
            
            # Method 2: Extract from 'id=' parameter (fallback)
            if 'id=' in url:
                id_match = re.search(r'id=([^&]*)', url)
                if id_match:
                    id_value = urllib.parse.unquote(id_match.group(1))
                    if '/' in id_value:
                        potential_filename = id_value.split('/')[-1]
                        if '.' in potential_filename:
                            print(f"🔍 Debug: Filename from id parameter: {potential_filename}")
                            return potential_filename
            
            # Method 3: Look for filename patterns in the entire URL
            filename_patterns = [
                r'/([^/]+\.(rar|zip|pdf|docx?|xlsx?|pptx?|mp[34]|avi|mkv|mov|wmv|flv|webm|m4v))(?:\?|$)',
                r'([^/\s]+\.(rar|zip|pdf|docx?|pptx?|mp[34]|avi|mkv|mov|wmv|flv|webm|m4v))(?:\?|$)'
            ]
            
            for pattern in filename_patterns:
                matches = re.findall(pattern, url, re.IGNORECASE)
                if matches:
                    filename = matches[-1][0] if isinstance(matches[-1], tuple) else matches[-1]
                    print(f"🔍 Debug: Filename from pattern matching: {filename}")
                    return filename
            
            # Default fallback
            print("🔍 Debug: No filename found, using default")
            return "sharepoint_download.rar"
            
        except Exception as e:
            print(f"🔍 Debug: Error in extract_filename_from_url: {e}")
            return "sharepoint_download_error.rar"
    
    def create_multiple_download_urls(self, sharing_url):
        """
        Create multiple potential download URLs from SharePoint sharing URL
        """
        download_urls = []
        
        try:
            import urllib.parse
            
            if ':u:/r/' in sharing_url:
                parts = sharing_url.split(':u:/r/')
                if len(parts) == 2:
                    base_url = parts[0]
                    path_part = parts[1]
                    
                    # Remove query parameters for clean path
                    clean_path = path_part.split('?')[0] if '?' in path_part else path_part
                    
                    # Method 1: Direct file access
                    direct_url = f"{base_url.rstrip('/')}/{clean_path}"
                    download_urls.append(direct_url)
                    
                    # Method 2: Add download parameter
                    download_param_url = f"{base_url.rstrip('/')}/{clean_path}?download=1"
                    download_urls.append(download_param_url)
                    
                    # Method 3: Force download with different parameter
                    force_download_url = f"{base_url.rstrip('/')}/{clean_path}?download=true&noRedirect=true"
                    download_urls.append(force_download_url)
                    
                    # Method 4: Use download.aspx with proper encoding
                    if 'personal/' in clean_path:
                        source_url = f"{base_url.rstrip('/')}/{clean_path}"
                        download_aspx_url = f"{base_url.rstrip('/')}/_layouts/15/download.aspx?SourceUrl={urllib.parse.quote(source_url)}"
                        download_urls.append(download_aspx_url)
                    
                    # Method 5: Use guestaccess.aspx for shared files
                    guest_url = f"{base_url.rstrip('/')}/_layouts/15/guestaccess.aspx?docid={urllib.parse.quote(clean_path)}&authkey=&e="
                    download_urls.append(guest_url)
                    
                    # Method 6: Try SharePoint API approach
                    try:
                        # Extract site path for API
                        if 'personal/' in clean_path:
                            site_path = clean_path.split('personal/')[1].split('/')[0]
                            api_path = clean_path.split('personal/')[1]
                            api_url = f"{base_url.rstrip('/')}/_api/v2.0/drives/b!{site_path}/root:/{api_path}:/content"
                            download_urls.append(api_url)
                    except Exception as e:
                        print(f"🔍 Debug: Error creating API URL: {e}")
                    
                    # Method 7: Try direct file access with different encoding
                    try:
                        # URL encode the path properly
                        encoded_path = urllib.parse.quote(clean_path, safe='')
                        direct_encoded_url = f"{base_url.rstrip('/')}/{encoded_path}"
                        download_urls.append(direct_encoded_url)
                    except Exception as e:
                        print(f"🔍 Debug: Error creating encoded URL: {e}")
                    
                    # Method 8: Try SharePoint modern download approach
                    try:
                        if 'personal/' in clean_path:
                            # Use modern SharePoint download pattern
                            modern_url = f"{base_url.rstrip('/')}/_layouts/15/download.aspx?UniqueId={urllib.parse.quote(clean_path)}&SourceUrl={urllib.parse.quote(f'{base_url.rstrip('/')}/{clean_path}')}"
                            download_urls.append(modern_url)
                    except Exception as e:
                        print(f"🔍 Debug: Error creating modern URL: {e}")
                    
                    # Method 9: Try SharePoint file preview approach
                    try:
                        if 'personal/' in clean_path:
                            # Use file preview pattern that often leads to download
                            preview_url = f"{base_url.rstrip('/')}/_layouts/15/filepreview.aspx?SourceUrl={urllib.parse.quote(f'{base_url.rstrip('/')}/{clean_path}')}"
                            download_urls.append(preview_url)
                    except Exception as e:
                        print(f"🔍 Debug: Error creating preview URL: {e}")
            
            print(f"🔍 Debug: Created {len(download_urls)} download URLs")
            for i, url in enumerate(download_urls):
                print(f"🔍 Debug: URL #{i+1}: {url[:100]}...")
            
            return download_urls
            
        except Exception as e:
            print(f"🔍 Debug: Error creating download URLs: {e}")
            return []
    
    def download_from_url(self, url, output_folder, filename, session, status_callback):
        """
        Download file from URL with proper validation and progress tracking
        """
        try:
            # Setup SharePoint-specific headers with proper authentication
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/octet-stream,application/rar,application/zip,application/pdf,application/octet-stream,*/*',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://moithuvemmo-my.sharepoint.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Upgrade-Insecure-Requests': '1',
                'X-Requested-With': 'XMLHttpRequest',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',
                'Origin': 'https://moithuvemmo-my.sharepoint.com',
                'Sec-Fetch-User': '?1'
            }
            
            # Initialize SharePoint session first (important for authentication)
            try:
                # First, visit the main SharePoint site to establish session
                init_url = url.split('/:u:/r/')[0] if ':u:/r/' in url else url
                print(f"🔍 Debug: Initializing session with: {init_url}")
                
                init_response = session.get(init_url, headers=headers, timeout=30)
                print(f"🔍 Debug: Session init status: {init_response.status_code}")
                
                # Wait a bit for session to establish
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"🔍 Debug: Session initialization failed: {e}")
            
            # Make request with established session
            response = session.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)
            
            print(f"🔍 Debug: Response status: {response.status_code}")
            print(f"🔍 Debug: Response headers: {dict(list(response.headers.items())[:5])}")
            
            # Check if response is successful
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                content_length = response.headers.get('content-length')
                
                # Validate this is actually a file download, not an HTML page
                if 'text/html' in content_type:
                    print(f"🔍 Debug: Received HTML page, not file download")
                    print(f"🔍 Debug: Content-Type: {content_type}")
                    print(f"🔍 Debug: Content-Length: {content_length}")
                    
                    # Check if this might be a redirect page
                    if 'redirect' in response.text.lower() or 'window.location' in response.text.lower():
                        print(f"🔍 Debug: Detected redirect page, following...")
                        # Try to extract redirect URL
                        import re
                        redirect_match = re.search(r'window\.location\s*=\s*["\']([^"\']+)["\']', response.text)
                        if redirect_match:
                            redirect_url = redirect_match.group(1)
                            print(f"🔍 Debug: Found redirect URL: {redirect_url}")
                            # Follow redirect
                            response = session.get(redirect_url, headers=headers, stream=True, timeout=60)
                            if response.status_code == 200:
                                content_type = response.headers.get('content-type', '').lower()
                                if 'text/html' not in content_type:
                                    print(f"🔍 Debug: Redirect successful, now downloading file")
                                else:
                                    print(f"🔍 Debug: Redirect still leads to HTML page")
                                    return False
                            else:
                                return False
                    
                    # Check for SharePoint-specific patterns that might indicate file access
                    elif 'access denied' in response.text.lower() or 'sign in' in response.text.lower():
                        print(f"🔍 Debug: SharePoint access denied - authentication required")
                        return False
                    elif 'file not found' in response.text.lower() or '404' in response.text.lower():
                        print(f"🔍 Debug: SharePoint file not found")
                        return False
                    elif 'sharepoint' in response.text.lower() and 'error' in response.text.lower():
                        print(f"🔍 Debug: SharePoint error page detected")
                        return False
                    else:
                        print(f"🔍 Debug: Unknown HTML page, analyzing content...")
                        # Try to extract any file-related information
                        if 'download' in response.text.lower() or 'file' in response.text.lower():
                            print(f"🔍 Debug: Page contains download/file references, might be accessible")
                            # Don't immediately fail, some SharePoint pages contain file info
                        else:
                            return False
                
                # Check content length
                total_size = int(content_length) if content_length else 0
                if total_size == 0:
                    print(f"🔍 Debug: Content length is 0 or unknown")
                    # Don't immediately fail, some servers don't send content-length
                
                # Create output directory
                os.makedirs(output_folder, exist_ok=True)
                file_path = os.path.join(output_folder, filename)
                
                # Download with progress tracking
                downloaded = 0
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                status_callback(f"📥 Downloading: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", "blue")
                            else:
                                status_callback(f"📥 Downloading: {downloaded:,} bytes", "blue")
                
                # Validate download
                if downloaded > 0:
                    status_callback(f"✅ Download completed: {downloaded:,} bytes", "green")
                    return True
                else:
                    os.remove(file_path)  # Remove empty file
                    print(f"🔍 Debug: Downloaded 0 bytes, removing empty file")
                    return False
            else:
                print(f"🔍 Debug: HTTP {response.status_code}: {response.reason}")
                
                # Handle SharePoint-specific error responses
                if response.status_code == 403:
                    print(f"🔍 Debug: Access forbidden - authentication required")
                    # Try to extract error message from response
                    if 'text/html' in response.headers.get('content-type', ''):
                        if 'access denied' in response.text.lower():
                            print(f"🔍 Debug: Access denied message detected")
                        elif 'sign in' in response.text.lower():
                            print(f"🔍 Debug: Sign-in required message detected")
                
                elif response.status_code == 404:
                    print(f"🔍 Debug: File not found")
                
                elif response.status_code == 401:
                    print(f"🔍 Debug: Unauthorized - invalid or expired cookies")
                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"🔍 Debug: Request error: {e}")
            return False
        except Exception as e:
            print(f"🔍 Debug: Download error: {e}")
            return False
    
    def find_download_link(self, html_content, base_url):
        """Tìm download link trong HTML"""
        try:
            import re
            print(f"🔍 Debug: find_download_link - base_url: {base_url[:100]}...")
            print(f"🔍 Debug: HTML content length: {len(html_content)}")
            
            # Tìm các link có thể download
            download_patterns = [
                r'href=["\']([^"\']*\.(?:rar|zip|pdf|docx?|xlsx?|mp[34]|avi|mkv))["\']',
                r'href=["\']([^"\']*download[^"\']*)["\']',
                r'href=["\']([^"\']*_layouts/15/download[^"\']*)["\']',
                r'href=["\']([^"\']*_layouts/15/onedrive\.aspx[^"\']*)["\']',
                r'href=["\']([^"\']*_layouts/15/guestaccess\.aspx[^"\']*)["\']',
                r'href=["\']([^"\']*_layouts/15/start\.aspx[^"\']*)["\']',
                r'href=["\']([^"\']*_layouts/15/viewlsts\.aspx[^"\']*)["\']',
            ]
            
            for i, pattern in enumerate(download_patterns):
                print(f"🔍 Debug: Pattern {i+1}: {pattern}")
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                print(f"🔍 Debug: Matches for pattern {i+1}: {matches}")
                
                for match in matches:
                    print(f"🔍 Debug: Processing match: {match}")
                    if match.startswith('http'):
                        print(f"🔍 Debug: Found absolute URL: {match}")
                        return match
                    elif match.startswith('/'):
                        # Tạo absolute URL
                        from urllib.parse import urljoin
                        absolute_url = urljoin(base_url, match)
                        print(f"🔍 Debug: Created absolute URL: {absolute_url}")
                        return absolute_url
            
            # Tìm kiếm nâng cao: Tìm các button hoặc link có text liên quan đến download
            advanced_patterns = [
                r'<a[^>]*download[^>]*href=["\']([^"\']+)["\'][^>]*>',
                r'<button[^>]*onclick=["\'][^"\']*download[^"\']*["\'][^>]*>',
                r'<input[^>]*type=["\']button["\'][^>]*onclick=["\'][^"\']*download[^"\']*["\'][^>]*>',
            ]
            
            for i, pattern in enumerate(advanced_patterns):
                print(f"🔍 Debug: Advanced Pattern {i+1}: {pattern}")
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                print(f"🔍 Debug: Advanced Matches for pattern {i+1}: {matches}")
                
                for match in matches:
                    print(f"🔍 Debug: Processing advanced match: {match}")
                    if match.startswith('http'):
                        print(f"🔍 Debug: Found advanced absolute URL: {match}")
                        return match
                    elif match.startswith('/'):
                        from urllib.parse import urljoin
                        absolute_url = urljoin(base_url, match)
                        print(f"🔍 Debug: Created advanced absolute URL: {absolute_url}")
                        return absolute_url
            
            print("🔍 Debug: Không tìm thấy download link nào")
            return None
        except Exception as e:
            print(f"🔍 Debug: Error in find_download_link: {e}")
            return None
    
    def download_from_direct_link(self, download_link, output_folder, filename, cookie_file, status_callback):
        """Tải file từ direct link"""
        try:
            import requests
            
            status_callback(f"📥 Đang tải file từ direct link...", "blue")
            
            # Headers để giả lập browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://moithuvemmo-my.sharepoint.com/',
            }
            
            # Xử lý cookies nếu có
            cookies = None
            if cookie_file and os.path.exists(cookie_file):
                try:
                    from utils.cookies import load_cookies_from_file
                    cookies = load_cookies_from_file(cookie_file)
                    print(f"🔍 Debug: Loaded cookies from: {cookie_file}")
                except Exception as e:
                    print(f"🔍 Debug: Error loading cookies: {e}")
            
            # Tải file với cookies và headers
            response = requests.get(download_link, headers=headers, cookies=cookies, stream=True, timeout=60)
            response.raise_for_status()
            
            # Lấy kích thước file
            total_size = int(response.headers.get('content-length', 0))
            
            # Tạo đường dẫn file
            file_path = os.path.join(output_folder, filename)
            
            # Tải file với progress
            downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            status_callback(f"📥 Đang tải: {percent:.1f}% ({downloaded}/{total_size} bytes)", "blue")
                else:
                            status_callback(f"📥 Đang tải: {downloaded} bytes", "blue")
            
            status_callback(f"✅ Hoàn tất tải file: {filename}", "green")
            return True
            
        except Exception as e:
            status_callback(f"❌ Lỗi tải từ direct link: {str(e)}", "red")
            return False
    
    def download_sharepoint_direct(self, url, output_folder, filename, cookie_file, status_callback):
        """Phương pháp download SharePoint trực tiếp"""
        try:
            print(f"🔍 Debug: download_sharepoint_direct - URL: {url[:100]}...")
            status_callback("🔍 Thử phương pháp SharePoint trực tiếp...", "blue")
            
            # Tạo URL download trực tiếp cho SharePoint
            if ':u:/r/' in url:
                # Chuyển đổi sharing URL thành download URL
                download_url = self.create_sharepoint_download_url(url)
                if download_url:
                    print(f"🔍 Debug: Created download URL: {download_url[:100]}...")
                    status_callback("🔗 Đã tạo download URL, đang tải...", "green")
                    
                    # Tải file trực tiếp
                    return self.download_from_direct_link(download_url, output_folder, filename, cookie_file, status_callback)
            
            # Nếu không phải sharing URL, thử phương pháp khác
            if '_layouts/15/onedrive.aspx' in url:
                # Tạo URL download từ OneDrive
                download_url = self.create_onedrive_download_url(url)
                if download_url:
                    print(f"🔍 Debug: Created OneDrive download URL: {download_url[:100]}...")
                    status_callback("🔗 Đã tạo OneDrive download URL, đang tải...", "green")
                    
                    # Tải file trực tiếp
                    return self.download_from_direct_link(download_url, output_folder, filename, cookie_file, status_callback)
            
            print("🔍 Debug: Không thể tạo download URL")
            return False
            
        except Exception as e:
            print(f"🔍 Debug: Error in download_sharepoint_direct: {e}")
            status_callback(f"❌ Lỗi phương pháp SharePoint trực tiếp: {str(e)}", "red")
            return False
    
    def download_sharepoint_file_multi_approach(self, sharing_url, output_folder, cookie_file, status_callback):
        """Try multiple approaches to download SharePoint files"""
        filename = self.extract_filename_from_url(sharing_url)
        session = requests.Session()
        
        # Load cookies if available
        if cookie_file and os.path.exists(cookie_file):
            try:
                from utils.cookies import load_cookies_from_file
                cookies = load_cookies_from_file(cookie_file)
                if cookies:
                    session.cookies.update(cookies)
                    status_callback("🍪 Cookies loaded successfully", "green")
            except Exception as e:
                status_callback(f"Warning: Could not load cookies: {e}", "orange")
        
        # Approach 1: Graph API
        status_callback("🔄 Trying Microsoft Graph API...", "blue")
        if self.try_graph_api_download(sharing_url, output_folder, filename, session, status_callback):
            return True
        
        # Approach 2: Direct page parsing
        status_callback("🔄 Trying direct page parsing...", "blue")
        if self.try_page_parsing_download(sharing_url, output_folder, filename, session, status_callback):
            return True
        
        # Approach 3: URL manipulation
        status_callback("🔄 Trying URL manipulation...", "blue")
        if self.try_url_manipulation_download(sharing_url, output_folder, filename, session, status_callback):
            return True
        
        # Approach 4: yt-dlp with special config
        status_callback("🔄 Trying yt-dlp as final fallback...", "blue")
        return self.try_ytdlp_sharepoint(sharing_url, output_folder, cookie_file, status_callback)
    
    def try_graph_api_download(self, sharing_url, output_folder, filename, session, status_callback):
        """Try downloading using Microsoft Graph API"""
        try:
            graph_url = self.create_sharepoint_api_url(sharing_url)
            if not graph_url:
                return False
            
            # Add Microsoft Graph headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Authorization': 'Bearer anonymous'  # For public shares
            }
            
            response = session.get(graph_url, headers=headers, stream=True, timeout=60)
            
            if response.status_code == 200:
                return self.save_file_with_progress(response, output_folder, filename, status_callback)
            
            return False
        except Exception as e:
            status_callback(f"Graph API failed: {str(e)}", "orange")
            return False
    
    def try_page_parsing_download(self, sharing_url, output_folder, filename, session, status_callback):
        """Try downloading by parsing SharePoint page content"""
        try:
            download_url = self.get_sharepoint_download_url_from_page(sharing_url, session, status_callback)
            if download_url:
                response = session.get(download_url, stream=True, timeout=60)
                if response.status_code == 200:
                    return self.save_file_with_progress(response, output_folder, filename, status_callback)
            return False
        except Exception as e:
            status_callback(f"Page parsing failed: {str(e)}", "orange")
            return False
    
    def try_url_manipulation_download(self, sharing_url, output_folder, filename, session, status_callback):
        """Try downloading using URL manipulation methods"""
        try:
            # Try simple download URL
            simple_url = self.create_simple_download_url(sharing_url)
            if simple_url:
                response = session.get(simple_url, stream=True, timeout=60)
                if response.status_code == 200:
                    return self.save_file_with_progress(response, output_folder, filename, status_callback)
            
            # Try direct file URL
            direct_url = self.create_direct_file_url(sharing_url)
            if direct_url:
                response = session.get(direct_url, stream=True, timeout=60)
                if response.status_code == 200:
                    return self.save_file_with_progress(response, output_folder, filename, status_callback)
            
            return False
        except Exception as e:
            status_callback(f"URL manipulation failed: {str(e)}", "orange")
            return False
    
    def try_ytdlp_sharepoint(self, sharing_url, output_folder, cookie_file, status_callback):
        """Try downloading using yt-dlp as final fallback"""
        try:
            status_callback("🔄 Using yt-dlp fallback method...", "blue")
            return self.download_onedrive_file(sharing_url, output_folder, cookie_file, status_callback)
        except Exception as e:
            status_callback(f"yt-dlp fallback failed: {str(e)}", "orange")
            return False
    
    def handle_sharepoint_error_response(self, response, status_callback):
        """Handle SharePoint-specific error responses"""
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error'].get('message', 'Unknown SharePoint error')
                    error_code = error_data['error'].get('code', 'Unknown')
                    status_callback(f"SharePoint API Error: {error_code} - {error_msg}", "red")
                    
                    # Provide specific guidance based on error code
                    if error_code == 'InvalidRequest':
                        status_callback("💡 Try: Check if the sharing link is still valid", "blue")
                    elif error_code == 'InvalidRequest':
                        status_callback("💡 Try: Ensure cookies are valid and up-to-date", "blue")
                    elif error_code == 'NotFound':
                        status_callback("💡 Try: Verify the file path in the sharing URL", "blue")
                        
                    return False
        except Exception:
            pass
        
        # Generic HTTP error handling
        status_callback(f"HTTP {response.status_code}: {response.reason}", "red")
        if response.status_code == 403:
            status_callback("💡 Authentication required - check cookies", "blue")
        elif response.status_code == 404:
            status_callback("💡 File not found - check sharing URL", "blue")
        elif response.status_code == 400:
            status_callback("💡 Bad request - trying alternative methods", "blue")
        
        return False
    
    def save_file_with_progress(self, response, output_folder, filename, status_callback):
        """Save file with progress tracking and validation"""
        try:
            total_size = int(response.headers.get('content-length', 0))
            file_path = os.path.join(output_folder, filename)
            
            # Ensure directory exists
            os.makedirs(output_folder, exist_ok=True)
            
            downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            status_callback(f"📥 Downloading: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", "blue")
                        else:
                            status_callback(f"📥 Downloading: {downloaded:,} bytes", "blue")
            
            # Validate file was actually downloaded
            if downloaded == 0:
                os.remove(file_path)  # Remove empty file
                status_callback("❌ Downloaded file is empty - removing", "red")
                return False
            
            status_callback(f"✅ Successfully downloaded: {filename} ({downloaded:,} bytes)", "green")
            return True
            
        except Exception as e:
            status_callback(f"Error saving file: {str(e)}", "red")
            return False
    
    def create_sharepoint_download_url(self, sharing_url):
        """
        Create proper SharePoint download URL from sharing URL
        Handle :u:/r/ format correctly
        """
        try:
            import urllib.parse
            print(f"🔍 Debug: create_sharepoint_download_url - input: {sharing_url[:100]}...")
            
            if ':u:/r/' in sharing_url:
                # Split the URL properly
                parts = sharing_url.split(':u:/r/')
                if len(parts) == 2:
                    base_url = parts[0].rstrip('/')
                    path_part = parts[1]
                    
                    # Parse the path to extract file information
                    decoded_path = urllib.parse.unquote(path_part)
                    print(f"🔍 Debug: decoded_path: {decoded_path[:100]}...")
                    
                    # Create SharePoint API download URL
                    # Format: https://domain.sharepoint.com/_api/v2.0/...
                    if 'personal/' in path_part:
                        # Extract personal site path
                        personal_path = path_part.split('personal/')[1]
                        site_path = personal_path.split('/')[0]
                        
                        # Construct API download URL
                        api_url = f"{base_url}/_api/v2.0/drives/b!{site_path}/root:/{decoded_path}:/content"
                        print(f"🔍 Debug: Created API download URL: {api_url[:100]}...")
                        return api_url
                    
                    # Fallback: Create direct download URL
                    download_url = f"{base_url}/personal/{path_part}/_layouts/15/download.aspx"
                    print(f"🔍 Debug: Created fallback download URL: {download_url[:100]}...")
                    return download_url
                
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in create_sharepoint_download_url: {e}")
            return None
    
    def create_onedrive_download_url(self, onedrive_url):
        """Tạo download URL từ OneDrive URL"""
        try:
            print(f"🔍 Debug: create_onedrive_download_url - input: {onedrive_url[:100]}...")
            
            # Format: .../_layouts/15/onedrive.aspx?id=...&parent=...
            if '_layouts/15/onedrive.aspx' in onedrive_url:
                # Thay thế onedrive.aspx bằng download.aspx
                download_url = onedrive_url.replace('onedrive.aspx', 'download.aspx')
                print(f"🔍 Debug: Created OneDrive download URL: {download_url[:100]}...")
                return download_url
            
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in create_onedrive_download_url: {e}")
            return None
    
    def convert_sharepoint_sharing_url(self, sharing_url):
        """Chuyển đổi SharePoint sharing URL thành URL download"""
        try:
            print(f"🔍 Debug: convert_sharepoint_sharing_url - input: {sharing_url[:100]}...")
            
            # Format: https://domain.sharepoint.com/:u:/r/personal/.../Documents/.../filename.rar
            if ':u:/r/' in sharing_url:
                # Tách URL thành các phần
                base_parts = sharing_url.split(':u:/r/')
                if len(base_parts) == 2:
                    base_url = base_parts[0]
                    path_part = base_parts[1]
                    
                    # Tìm phần Documents trong path
                    if 'Documents' in path_part:
                        # Tạo URL mới với format OneDrive
                        new_url = f"{base_url}/personal/{path_part}"
                        print(f"🔍 Debug: Converted URL: {new_url[:100]}...")
                        return new_url
                    
                    # Nếu không có Documents, thử format khác
                    else:
                        # Tạo URL với _layouts/15/onedrive.aspx
                        new_url = f"{base_url}/personal/{path_part}/_layouts/15/onedrive.aspx"
                        print(f"🔍 Debug: Converted URL (onedrive): {new_url[:100]}...")
                        return new_url
            
            print("🔍 Debug: Không thể chuyển đổi SharePoint sharing URL")
            return None
            
        except Exception as e:
            print(f"🔍 Debug: Error in convert_sharepoint_sharing_url: {e}")
            return None
    
    def fallback_download_method(self, url, output_folder, filename, cookie_file, status_callback):
        """Phương pháp fallback cho SharePoint"""
        try:
            status_callback("🔄 Thử phương pháp fallback...", "blue")
            
            # Thử sử dụng yt-dlp với cấu hình đặc biệt
            import yt_dlp
            
            ydl_opts = {
                'outtmpl': os.path.join(output_folder, f'{filename}.%(ext)s'),
                'quiet': False,
                'noplaylist': True,
                'restrictfilenames': False,
                'retries': 10,
                'socket_timeout': 120,
                'extractor_retries': 10,
                'ignoreerrors': True,
                'no_warnings': False,
            }
            
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '').strip()
                    speed = d.get('_speed_str', '').strip()
                    if status_callback:
                        status_callback(f"📥 Đang tải: {percent} | Tốc độ: {speed}", "blue")
                elif d['status'] == 'finished':
                    if status_callback:
                        status_callback("✅ Hoàn tất tải file!", "green")
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_callback("🔍 Đang thử tải với yt-dlp...", "blue")
                ydl.download([url])
            
            return True
            
        except Exception as e:
            status_callback(f"❌ Fallback method cũng thất bại: {str(e)}", "red")
            return False

    def refresh_performance(self):
        """Làm mới báo cáo hiệu suất"""
        if not self.system_optimizer:
            return
            
        try:
            # Get performance report
            report = self.system_optimizer.get_performance_report()
            
            # Clear previous content
            self.perf_text.delete("1.0", tk.END)
            
            if 'error' not in report:
                perf_info = f"CPU Usage: {report['cpu']['usage_percent']}% ({report['cpu']['status']})\n"
                perf_info += f"Memory Usage: {report['memory']['usage_percent']}% ({report['memory']['status']})\n"
                perf_info += f"Disk Usage: {report['disk']['usage_percent']}% ({report['disk']['status']})\n"
                perf_info += f"Available Memory: {report['memory']['available_gb']:.1f} GB\n"
                perf_info += f"Free Disk Space: {report['disk']['free_gb']:.1f} GB\n\n"
                
                # Optimal settings
                optimal = self.system_optimizer.get_optimal_settings()
                perf_info += "⚡ Cài đặt tối ưu:\n"
                for key, value in optimal.items():
                    perf_info += f"  {key}: {value}\n"
                    
                # External downloaders
                downloaders = self.system_optimizer.check_external_downloaders()
                perf_info += "\n🔧 External Downloaders:\n"
                for name, available in downloaders.items():
                    status = "✅ Available" if available else "❌ Not available"
                    perf_info += f"  {name}: {status}\n"
            else:
                perf_info = f"Error: {report['error']}"
                
            self.perf_text.insert("1.0", perf_info)
            
        except Exception as e:
            self.perf_text.delete("1.0", tk.END)
            self.perf_text.insert("1.0", f"Error refreshing performance: {e}")

    def load_optimization_tips(self):
        """Tải mẹo tối ưu hóa"""
        if not self.system_optimizer:
            return
            
        try:
            tips = self.system_optimizer.get_network_optimization_tips()
            
            # Clear previous content
            self.tips_text.delete("1.0", tk.END)
            
            tips_text = "🌐 Mẹo tối ưu hóa mạng:\n\n"
            for i, tip in enumerate(tips, 1):
                tips_text += f"{i}. {tip}\n"
                
            self.tips_text.insert("1.0", tips_text)
            
        except Exception as e:
            self.tips_text.delete("1.0", tk.END)
            self.tips_text.insert("1.0", f"Error loading tips: {e}")
    
    def provide_manual_download_guidance(self, url, status_callback):
        """
        Provide manual download instructions when automated methods fail
        """
        status_callback("💡 Manual Download Instructions:", "blue")
        status_callback("1. Open the SharePoint URL in your browser", "blue")
        status_callback("2. Sign in to your Microsoft account if required", "blue")
        status_callback("3. Click the Download button or right-click → Save As", "blue")
        status_callback("4. Check if the file requires special permissions", "blue")
        status_callback("", "blue")
        status_callback("🔧 Troubleshooting Tips:", "blue")
        status_callback("• Update your cookies file if authentication is required", "blue")
        status_callback("• Verify the sharing link hasn't expired", "blue")
        status_callback("• Try downloading a smaller file first to test access", "blue")
    
    def extract_download_links_from_page(self, url, session, status_callback):
        """Extract download links from SharePoint page content"""
        try:
            # Get the page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': url,
            }
            
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML to find download links
            import re
            
            # Look for download.aspx links
            download_patterns = [
                r'href=["\']([^"\']*download\.aspx[^"\']*)["\']',
                r'href=["\']([^"\']*downloadRedirect[^"\']*)["\']',
                r'"downloadUrl":\s*"([^"]*)"',
                r'"@microsoft.graph.downloadUrl":\s*"([^"]*)"'
            ]
            
            download_links = []
            for pattern in download_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        download_links.append(match)
                    elif match.startswith('/'):
                        from urllib.parse import urljoin
                        absolute_url = urljoin(url, match)
                        download_links.append(absolute_url)
            
            print(f"🔍 Debug: Found {len(download_links)} download links")
            return download_links
            
        except Exception as e:
            status_callback(f"Error parsing SharePoint page: {str(e)}", "orange")
            return []
    
    def ytdlp_sharepoint_download(self, url, output_folder, filename, cookie_file, status_callback):
        """Use yt-dlp as final fallback for SharePoint downloads"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'outtmpl': os.path.join(output_folder, filename),
                'quiet': False,
                'noplaylist': True,
                'restrictfilenames': False,
                'retries': 10,
                'socket_timeout': 120,
                'extractor_retries': 10,
                'ignoreerrors': True,
                'no_warnings': False,
            }
            
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '').strip()
                    speed = d.get('_speed_str', '').strip()
                    if status_callback:
                        status_callback(f"📥 Đang tải: {percent} | Tốc độ: {speed}", "blue")
                elif d['status'] == 'finished':
                    if status_callback:
                        status_callback("✅ Hoàn tất tải file!", "green")
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_callback("🔍 Đang thử tải với yt-dlp...", "blue")
                ydl.download([url])
            
            return True
            
        except Exception as e:
            status_callback(f"❌ yt-dlp fallback failed: {str(e)}", "red")
            return False
