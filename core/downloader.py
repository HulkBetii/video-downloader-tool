# core/downloader.py
import os
import subprocess
import sys
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from .config import DOWNLOAD_CONFIG, POST_PROCESSORS, SPEED_OPTIMIZED_CONFIG, QUALITY_OPTIMIZED_CONFIG, FFMPEG_CONFIG, SAFE_FALLBACK_CONFIG, auto_adjust_config_for_stability

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


def cleanup_temp_files(output_folder):
    """
    Clean up temporary fragment files that might cause download issues
    """
    try:
        import glob
        # Look for common temporary file patterns
        temp_patterns = [
            '*.part*',
            '*.fragment*',
            '*.tmp',
            '*.temp',
            '*~',
            '*.part-Frag*',
            '*.ytdl',
            '*.ytdlp',
            '*.f*',  # Fragment files
            '*.m4s',  # Audio/video segments
            '*.ts',   # Transport stream segments
        ]
        
        for pattern in temp_patterns:
            temp_files = glob.glob(os.path.join(output_folder, pattern))
            for temp_file in temp_files:
                try:
                    if os.path.isfile(temp_file):
                        # Check if file is old (more than 1 hour) to avoid deleting active downloads
                        import time
                        file_age = time.time() - os.path.getmtime(temp_file)
                        if file_age > 3600:  # 1 hour
                            os.remove(temp_file)
                except Exception:
                    pass  # Ignore errors when cleaning up
                    
    except Exception:
        pass  # Ignore cleanup errors


def preprocess_url(url):
    """
    Preprocess URL to handle common issues
    """
    try:
        # Remove whitespace
        url = url.strip()
        
        # Handle common URL issues
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove problematic characters
        url = url.replace('\n', '').replace('\r', '').replace('\t', '')
        
        # Handle YouTube mobile URLs
        if 'youtube.com' in url and '/m.' in url:
            url = url.replace('/m.', '/www.')
        
        return url
        
    except Exception:
        return url


def validate_download_config(url, config, status_callback=None):
    """
    Validate download configuration and URL before attempting download
    """
    try:
        # Basic URL validation
        if not url or not url.strip():
            if status_callback:
                status_callback("❌ URL không hợp lệ", "red")
            return False
        
        # Check for problematic URL patterns
        url_lower = url.lower()
        problematic_patterns = [
            'javascript:', 'data:', 'file://', 'ftp://'
        ]
        
        for pattern in problematic_patterns:
            if pattern in url_lower:
                if status_callback:
                    status_callback(f"❌ URL không được hỗ trợ: {pattern}", "red")
                return False
        
        # Validate configuration
        if not config:
            if status_callback:
                status_callback("❌ Cấu hình download không hợp lệ", "red")
            return False
        
        # Check for reasonable fragment settings
        concurrent_frags = config.get('concurrent_fragment_downloads', 1)
        if concurrent_frags > 8:
            if status_callback:
                status_callback("⚠️ Cảnh báo: Số fragment đồng thời quá cao, có thể gây lỗi", "orange")
        
        return True
        
    except Exception as e:
        if status_callback:
            status_callback(f"❌ Lỗi kiểm tra cấu hình: {str(e)}", "red")
        return False


def download_video(url, output_folder, cookie_file=None, status_callback=None, optimize_mode='balanced', max_retries=2):
    """
    Tải video từ URL, sử dụng yt-dlp
    :param url: Đường dẫn video
    :param output_folder: Thư mục lưu video
    :param cookie_file: File cookies.txt hoặc .json nếu cần
    :param status_callback: Hàm callback để cập nhật trạng thái cho UI
    :param optimize_mode: Chế độ tối ưu hóa ('balanced', 'speed', 'quality')
    :param max_retries: Số lần thử lại tối đa khi gặp lỗi file
    """
    
    # Preprocess URL to handle common issues
    original_url = url
    url = preprocess_url(url)
    
    if status_callback and url != original_url:
        status_callback(f"🔧 URL đã được xử lý: {url[:50]}...", "blue")
    
    # Kiểm tra ffmpeg
    ffmpeg_available = check_ffmpeg_available()
    
    # Chọn cấu hình dựa trên mode và ffmpeg availability
    if optimize_mode == 'speed':
        config = SPEED_OPTIMIZED_CONFIG.copy()
    elif optimize_mode == 'quality':
        config = QUALITY_OPTIMIZED_CONFIG.copy()

    else:
        config = DOWNLOAD_CONFIG.copy()
    
    # Lưu mode gốc để có thể fallback nếu cần
    original_mode = optimize_mode
    
    # Auto-adjust configuration for better stability
    config = auto_adjust_config_for_stability(config, url)
    
    # Validate configuration before proceeding
    if not validate_download_config(url, config, status_callback):
        if status_callback:
            status_callback("❌ Không thể tiếp tục do cấu hình không hợp lệ", "red")
        return False
    
    # Nếu có ffmpeg và muốn sử dụng, thêm cấu hình ffmpeg
    if ffmpeg_available and optimize_mode in ['quality']:
        config.update(FFMPEG_CONFIG)
        if status_callback:
            status_callback("✅ Sử dụng ffmpeg để merge video", "green")
    else:
        if status_callback and not ffmpeg_available and optimize_mode in ['quality']:
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
        elif d['status'] == 'error':
            # Xử lý lỗi fragment cụ thể
            error_msg = d.get('error', '')
            if 'fragment' in error_msg.lower() and status_callback:
                status_callback("⚠️ Phát hiện lỗi fragment, đang thử khắc phục...", "orange")

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
        
        # Cải thiện xử lý fragment để tránh lỗi
        'fragment_retries': config.get('fragment_retries', 5),  # Sử dụng config từ mode
        'retry_sleep': config.get('retry_sleep', 2),       # Sử dụng config từ mode
        'file_access_retries': config.get('file_access_retries', 5), # Sử dụng config từ mode
        'skip_unavailable_fragments': config.get('skip_unavailable_fragments', True), # Bỏ qua fragment không có sẵn
        
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
            # Clean up any existing temporary files before starting
            if attempt_number == 1:
                cleanup_temp_files(output_folder)
            
            # Thêm delay trước khi bắt đầu download để tránh race condition
            if attempt_number > 1:
                import time
                time.sleep(3)
            
            # Log the configuration being used for debugging
            if status_callback and attempt_number == 1:
                status_callback(f"🔧 Cấu hình download: {ydl_opts.get('concurrent_fragment_downloads', 'N/A')} fragment đồng thời", "blue")
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True  # Thành công
        except DownloadError as e:
            error_msg = str(e)
            
            # Log the specific error for debugging
            if status_callback:
                status_callback(f"⚠️ Lỗi yt-dlp: {error_msg[:100]}...", "orange")
            
            # Xử lý các lỗi fragment cụ thể - mở rộng để bắt nhiều loại lỗi hơn
            fragment_errors = [
                "fragment 1 not found",
                "fragment not found",
                "No such file or directory",
                "fragment download failed",
                "unable to continue",
                "fragment",
                "segment",
                "chunk",
                "part",
                "download failed",
                "network error",
                "connection error",
                "timeout",
                "retry",
                "failed to download"
            ]
            
            is_fragment_error = any(err in error_msg.lower() for err in fragment_errors)
            
            if is_fragment_error and attempt_number < max_retries:
                if status_callback:
                    status_callback(f"⚠️ Lần thử {attempt_number}: Lỗi fragment, thử lại với cài đặt an toàn hơn...", "orange")
                
                # Giảm concurrent downloads và thử lại với cài đặt an toàn
                retry_opts = ydl_opts.copy()
                retry_opts['concurrent_fragment_downloads'] = max(1, retry_opts.get('concurrent_fragment_downloads', 4) // 2)
                retry_opts['fragment_retries'] = 10  # Tăng retry cho fragment
                retry_opts['retry_sleep'] = 3        # Tăng thời gian chờ
                retry_opts['file_access_retries'] = 8  # Tăng retry cho file access
                retry_opts['skip_unavailable_fragments'] = True  # Bỏ qua fragment không có sẵn
                

                
                # Thêm delay trước khi retry
                import time
                time.sleep(2)
                
                return attempt_download(retry_opts, attempt_number + 1)
            else:
                if status_callback:
                    if is_fragment_error:
                        status_callback("❌ Lỗi fragment: Không thể tải một số phần của video.", "red")
                        status_callback("💡 Thử giảm chế độ tối ưu hóa hoặc kiểm tra kết nối mạng.", "orange")
                        status_callback("💡 Nếu vẫn lỗi, thử chế độ 'Cân bằng' thay vì 'Chất lượng cao'.", "orange")
                        status_callback("🔧 Hệ thống đã thử tự động khắc phục và fallback về chế độ an toàn.", "blue")
                    else:
                        status_callback(f"❌ Không thể tải: {error_msg.splitlines()[0]}", "red")
                return False
        except Exception as e:
            # Catch any other unexpected errors
            error_msg = str(e)
            if status_callback:
                status_callback(f"❌ Lỗi không xác định: {error_msg[:100]}...", "red")
                status_callback("🔧 Đang thử khắc phục tự động...", "blue")
            
            # Try to recover from unexpected errors
            if attempt_number < max_retries:
                if status_callback:
                    status_callback(f"🔄 Lần thử {attempt_number}: Thử lại với cài đặt an toàn...", "orange")
                
                # Use safe fallback for unexpected errors
                safe_opts = {
                    'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                    'paths': {'home': output_folder, 'temp': output_folder},
                    'progress_hooks': [hook],
                    'windowsfilenames': True,
                    'restrictfilenames': True if os.name == 'nt' else False,
                    'trim_file_name': 120,
                    'continuedl': True,
                    'nopart': False,
                    'updatetime': False,
                    'writethumbnail': False,
                    **SAFE_FALLBACK_CONFIG,
                }
                
                # Add cookies if available
                if cookie_file:
                    if is_valid_cookie_file(cookie_file):
                        cookie_opts = convert_cookies_to_yt_dlp_format(cookie_file)
                        safe_opts.update(cookie_opts)
                
                return attempt_download(safe_opts, attempt_number + 1)
            
            if status_callback:
                status_callback("❌ Không thể khắc phục lỗi sau nhiều lần thử.", "red")
            return False

    # Thực hiện download với retry
    success = attempt_download(ydl_opts)
    
    # Nếu main download thất bại, thử các phương pháp thay thế
    if not success and status_callback:
        status_callback("🔄 Main download thất bại, thử các phương pháp thay thế...", "orange")
        
        # Try alternative download methods
        alt_success = try_alternative_download_methods(url, output_folder, cookie_file, status_callback)
        
        if alt_success:
            if status_callback:
                status_callback("✅ Download thành công với phương pháp thay thế!", "green")
            return True
        else:
            if status_callback:
                status_callback("❌ Tất cả các phương pháp download đều thất bại", "red")
            return False
    
    if success and status_callback:
        status_callback("✅ Hoàn tất tải video!", "green")
    
    return success


def try_alternative_download_methods(url, output_folder, cookie_file, status_callback):
    """
    Try alternative download methods when the main method fails
    """
    alternative_methods = [
        {
            'name': 'Chế độ đơn giản',
            'config': {
                'format': 'best[ext=mp4]/best',
                'concurrent_fragment_downloads': 1,
                'fragment_retries': 3,
                'retry_sleep': 2,
                'skip_unavailable_fragments': True,
                'prefer_ffmpeg': False,
            }
        },
        {
            'name': 'Chế độ audio-only',
            'config': {
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'concurrent_fragment_downloads': 1,
                'fragment_retries': 3,
                'retry_sleep': 2,
                'skip_unavailable_fragments': True,
                'prefer_ffmpeg': False,
            }
        },
        {
            'name': 'Chế độ tối thiểu',
            'config': {
                'format': 'worst[ext=mp4]/worst',
                'concurrent_fragment_downloads': 1,
                'fragment_retries': 5,
                'retry_sleep': 3,
                'skip_unavailable_fragments': True,
                'prefer_ffmpeg': False,
                'nocheckcertificate': True,
                'ignoreerrors': True,
            }
        }
    ]
    
    for method in alternative_methods:
        try:
            if status_callback:
                status_callback(f"🔄 Thử phương pháp: {method['name']}...", "blue")
            
            # Create options for this method
            method_opts = {
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'paths': {'home': output_folder, 'temp': output_folder},
                'windowsfilenames': True,
                'restrictfilenames': True if os.name == 'nt' else False,
                'trim_file_name': 120,
                'continuedl': True,
                'nopart': False,
                'updatetime': False,
                'writethumbnail': False,
                **method['config'],
            }
            
            # Add cookies if available
            if cookie_file:
                if is_valid_cookie_file(cookie_file):
                    cookie_opts = convert_cookies_to_yt_dlp_format(cookie_file)
                    method_opts.update(cookie_opts)
            
            # Try download with this method
            with YoutubeDL(method_opts) as ydl:
                ydl.download([url])
            
            if status_callback:
                status_callback(f"✅ Thành công với phương pháp: {method['name']}", "green")
            return True
            
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Phương pháp {method['name']} thất bại: {str(e)[:50]}...", "orange")
            continue
    
    if status_callback:
        status_callback("❌ Tất cả các phương pháp thay thế đều thất bại", "red")
    return False
