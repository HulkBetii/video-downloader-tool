# core/downloader.py
import os
import subprocess
import sys
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from .config import DOWNLOAD_CONFIG, POST_PROCESSORS, SPEED_OPTIMIZED_CONFIG, QUALITY_OPTIMIZED_CONFIG, SPEED_QUALITY_OPTIMIZED_CONFIG, FFMPEG_CONFIG

# Add the project root to the path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import cookie utilities with fallback
try:
    from utils.cookies import is_valid_cookie_file, convert_cookies_to_yt_dlp_format
except ImportError:
    # Fallback functions if cookie utilities can't be imported
    def is_valid_cookie_file(path):
        """Fallback: just check if file exists"""
        return os.path.exists(path) if path else False
    
    def convert_cookies_to_yt_dlp_format(cookie_path):
        """Fallback: return basic cookie format"""
        return {'cookiefile': cookie_path} if cookie_path else {}


def check_ffmpeg_available():
    """
    Kiểm tra xem ffmpeg có sẵn không
    """
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_video(url, output_folder, cookie_file=None, status_callback=None, optimize_mode='balanced', max_retries=2):
    """
    Tải video từ URL, sử dụng yt-dlp
    :param url: Đường dẫn video
    :param output_folder: Thư mục lưu video
    :param cookie_file: File cookies.txt hoặc .json nếu cần
    :param status_callback: Hàm callback để cập nhật trạng thái cho UI
    :param optimize_mode: Chế độ tối ưu hóa ('balanced', 'speed', 'quality', 'speed_quality')
    :param max_retries: Số lần thử lại tối đa khi gặp lỗi file
    """
    
    # Kiểm tra ffmpeg
    ffmpeg_available = check_ffmpeg_available()
    
    # Chọn cấu hình dựa trên mode và ffmpeg availability
    if optimize_mode == 'speed':
        config = SPEED_OPTIMIZED_CONFIG.copy()
    elif optimize_mode == 'quality':
        config = QUALITY_OPTIMIZED_CONFIG.copy()
    elif optimize_mode == 'speed_quality':
        # Chế độ mới: Tối ưu tốc độ + Chất lượng cao
        if ffmpeg_available:
            config = SPEED_QUALITY_OPTIMIZED_CONFIG.copy()
            if status_callback:
                status_callback("🚀 Chế độ Tốc độ + Chất lượng: Sử dụng ffmpeg để merge video chất lượng cao", "green")
        else:
            # Fallback về balanced nếu không có ffmpeg
            config = DOWNLOAD_CONFIG.copy()
            if status_callback:
                status_callback("⚠️ Chế độ Tốc độ + Chất lượng yêu cầu ffmpeg. Chuyển về chế độ Cân bằng.", "orange")
    else:
        config = DOWNLOAD_CONFIG.copy()
    
    # Nếu có ffmpeg và muốn sử dụng, thêm cấu hình ffmpeg
    if ffmpeg_available and optimize_mode in ['quality', 'speed_quality']:
        config.update(FFMPEG_CONFIG)
        if status_callback:
            status_callback("✅ Sử dụng ffmpeg để merge video", "green")
    else:
        if status_callback and not ffmpeg_available and optimize_mode in ['quality', 'speed_quality']:
            status_callback("⚠️ ffmpeg không có sẵn, sử dụng format đơn giản", "orange")

    def hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            
            # Thêm thông tin fragment
            fragment_info = ""
            if 'fragment_index' in d and 'fragment_count' in d:
                current_frag = d.get('fragment_index', 0)
                total_frags = d.get('fragment_count', 0)
                if total_frags > 0:
                    fragment_info = f" | Fragment: {current_frag}/{total_frags}"
            
            if status_callback:
                status_text = f"📥 Đang tải: {percent} | Tốc độ: {speed}"
                if eta:
                    status_text += f" | Còn lại: {eta}"
                if fragment_info:
                    status_text += fragment_info
                status_callback(status_text, "blue")
        elif d['status'] == 'finished':
            if status_callback:
                status_callback("✅ Hoàn tất tải video!", "green")

    # Đảm bảo thư mục lưu tồn tại trước khi tải
    try:
        os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        if status_callback:
            status_callback(f"❌ Không thể tạo thư mục lưu: {e}", "red")
        return

    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'paths': {'home': output_folder, 'temp': output_folder},
        'progress_hooks': [hook],
        # Tối ưu và an toàn cho Windows: tránh lỗi tên file/đường dẫn
        'windowsfilenames': True,
        'restrictfilenames': True if os.name == 'nt' else config.get('restrictfilenames', False),
        'trim_file_name': 120,  # giới hạn độ dài tên file
        'continuedl': True,     # tiếp tục tải nếu bị gián đoạn
        
        # Thêm cấu hình để tránh lỗi file
        'nopart': False,        # Giữ file tạm thời để có thể tiếp tục
        'updatetime': False,    # Không cập nhật thời gian file
        'writethumbnail': False, # Không tải thumbnail để tránh lỗi
        
        **config,
    }

    # Xử lý cookie file
    if cookie_file:
        if is_valid_cookie_file(cookie_file):
            cookie_opts = convert_cookies_to_yt_dlp_format(cookie_file)
            ydl_opts.update(cookie_opts)
            if status_callback:
                file_ext = os.path.splitext(cookie_file)[1].lower()
                status_callback(f"🍪 Sử dụng cookie file: {os.path.basename(cookie_file)} ({file_ext})", "blue")
        else:
            if status_callback:
                status_callback("⚠️ Cookie file không hợp lệ hoặc không tồn tại", "orange")

    # Hàm thực hiện download với retry
    def attempt_download(ydl_opts, attempt_number=1):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True  # Thành công
        except DownloadError as e:
            error_msg = str(e)
            if "No such file or directory" in error_msg and attempt_number < max_retries:
                if status_callback:
                    status_callback(f"⚠️ Lần thử {attempt_number}: Lỗi file tạm thời, thử lại với cài đặt an toàn hơn...", "orange")
                
                # Giảm concurrent downloads và thử lại
                retry_opts = ydl_opts.copy()
                retry_opts['concurrent_fragment_downloads'] = max(1, retry_opts.get('concurrent_fragment_downloads', 4) // 2)
                retry_opts['fragment_retries'] = 1  # Giảm retry cho fragment
                
                return attempt_download(retry_opts, attempt_number + 1)
            else:
                if status_callback:
                    if "No such file or directory" in error_msg:
                        status_callback("❌ Lỗi: Không thể tìm thấy file tạm thời. Có thể do quá nhiều fragment tải đồng thời.", "red")
                        status_callback("💡 Thử giảm chế độ tối ưu hóa hoặc kiểm tra kết nối mạng.", "orange")
                    else:
                        status_callback(f"❌ Không thể tải: {error_msg.splitlines()[0]}", "red")
                return False
        except FileNotFoundError as e:
            if status_callback:
                status_callback(f"❌ Lỗi file: {str(e)}", "red")
                status_callback("💡 Kiểm tra quyền truy cập thư mục và dung lượng ổ đĩa.", "orange")
            return False
        except PermissionError as e:
            if status_callback:
                status_callback(f"❌ Lỗi quyền truy cập: {str(e)}", "red")
                status_callback("💡 Chạy ứng dụng với quyền Administrator hoặc chọn thư mục khác.", "orange")
            return False
        except Exception as e:
            if status_callback:
                status_callback(f"⚠️ Lỗi không xác định: {str(e)}", "red")
                status_callback("💡 Thử khởi động lại ứng dụng hoặc kiểm tra cài đặt.", "orange")
            return False

    # Thực hiện download với retry
    success = attempt_download(ydl_opts)
    if success and status_callback:
        status_callback("✅ Hoàn tất tải video!", "green")
