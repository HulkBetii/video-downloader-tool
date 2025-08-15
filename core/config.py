# core/config.py
"""
Cấu hình cho video downloader
"""

# Cấu hình tối ưu hóa tốc độ tải
DOWNLOAD_CONFIG = {
    # Cấu hình format video - fallback nếu không có ffmpeg
    'format': 'best[ext=mp4]/best',  # Đơn giản hóa format để tránh cần merge
    'merge_output_format': 'mp4',
    'prefer_ffmpeg': False,  # Tắt ffmpeg để tránh lỗi
    
    # Tối ưu hóa tốc độ tải - giảm để tránh lỗi file
    'concurrent_fragment_downloads': 4,  # Giảm từ 8 xuống 4 để ổn định
    'buffersize': 1024,  # Buffer size (bytes)
    'http_chunk_size': 10485760,  # Chunk size 10MB
    'retries': 3,  # Số lần retry
    'fragment_retries': 3,  # Retry cho fragment
    'skip_unavailable_fragments': True,  # Bỏ qua fragment không có sẵn
    
    # Tối ưu hóa network
    'socket_timeout': 30,  # Timeout cho socket (giây)
    'extractor_retries': 3,  # Retry cho extractor
    'ignoreerrors': False,  # Không bỏ qua lỗi
    
    # Cấu hình khác
    'quiet': True,
    'noplaylist': True,
    'restrictfilenames': False,  # Cho phép Unicode (tên file tiếng Việt)
}

# Cấu hình post-processors - chỉ sử dụng nếu có ffmpeg
POST_PROCESSORS = []  # Bỏ post-processors để tránh lỗi ffmpeg

# Cấu hình cho các trường hợp đặc biệt
SPEED_OPTIMIZED_CONFIG = {
    **DOWNLOAD_CONFIG,
    'concurrent_fragment_downloads': 6,  # Giảm từ 16 xuống 6 để ổn định
    'buffersize': 2048,  # Tăng buffer size
    'http_chunk_size': 20971520,  # Tăng chunk size lên 20MB
}

# Cấu hình mới: Tối ưu tốc độ + Chất lượng cao
SPEED_QUALITY_OPTIMIZED_CONFIG = {
    **DOWNLOAD_CONFIG,
    # Giữ nguyên format chất lượng cao
    'format': 'bestvideo[height>=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'prefer_ffmpeg': True,  # Bật ffmpeg để merge video chất lượng cao
    
    # Tối ưu hóa tốc độ tải - giảm để tránh lỗi file
    'concurrent_fragment_downloads': 8,  # Giảm từ 20 xuống 8 để ổn định
    'buffersize': 4096,  # Tăng buffer size lên 4KB
    'http_chunk_size': 31457280,  # Tăng chunk size lên 30MB
    'retries': 5,  # Tăng số lần retry
    'fragment_retries': 5,  # Tăng retry cho fragment
    
    # Tối ưu hóa network nâng cao
    'socket_timeout': 20,  # Giảm timeout để tăng tốc độ
    'extractor_retries': 5,  # Tăng retry cho extractor
    
    # Cấu hình nâng cao cho tốc độ
    'max_downloads': 3,  # Cho phép tải nhiều video cùng lúc
    'max_sleep_interval': 0,  # Không delay giữa các request
    'sleep_interval': 0,  # Không sleep giữa các request
    'max_sleep_interval_requests': 0,  # Không sleep giữa các request
    
    # Tối ưu hóa memory
    'memory_limit': 0,  # Không giới hạn memory
    'max_filesize': 0,  # Không giới hạn kích thước file
    
    # Tối ưu hóa network nâng cao
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    },
    
    # Tối ưu hóa connection pooling
    'source_address': '0.0.0.0',  # Bind to all interfaces
    'force_ipv4': True,  # Ưu tiên IPv4 để tăng tốc độ
    'nocheckcertificate': True,  # Bỏ qua SSL check để tăng tốc độ
    
    # Tối ưu hóa fragment download - bỏ external downloader để tránh lỗi
    'hls_prefer_native': False,  # Sử dụng ffmpeg cho HLS
    # Bỏ external_downloader để tránh lỗi file management
}

QUALITY_OPTIMIZED_CONFIG = {
    **DOWNLOAD_CONFIG,
    # Ưu tiên video >=1080p, merge audio tốt nhất, fallback nếu không có
    'format': 'bestvideo[height>=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'concurrent_fragment_downloads': 3,  # Giảm từ 4 xuống 3 để ổn định
}

# Cấu hình cho trường hợp có ffmpeg
FFMPEG_CONFIG = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'prefer_ffmpeg': True,
    'restrictfilenames': False,  # Cho phép Unicode (tên file tiếng Việt)
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }]
}
