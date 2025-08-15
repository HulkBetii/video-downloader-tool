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

def auto_adjust_config_for_stability(config, url=None):
    """
    Automatically adjust configuration settings for better stability
    """
    adjusted_config = config.copy()
    
    # If URL contains known problematic sources, make settings more conservative
    if url:
        url_lower = url.lower()
        problematic_sources = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com'
        ]
        
        if any(source in url_lower for source in problematic_sources):
            # Make settings more conservative for problematic sources
            adjusted_config['concurrent_fragment_downloads'] = min(
                adjusted_config.get('concurrent_fragment_downloads', 4), 2
            )
            adjusted_config['fragment_retries'] = max(
                adjusted_config.get('fragment_retries', 5), 10
            )
            adjusted_config['retry_sleep'] = max(
                adjusted_config.get('retry_sleep', 2), 3
            )
            adjusted_config['socket_timeout'] = max(
                adjusted_config.get('socket_timeout', 30), 45
            )
    
    # General stability improvements
    if adjusted_config.get('concurrent_fragment_downloads', 1) > 4:
        adjusted_config['concurrent_fragment_downloads'] = 4
    
    if adjusted_config.get('fragment_retries', 1) < 5:
        adjusted_config['fragment_retries'] = 5
    
    if adjusted_config.get('retry_sleep', 0) < 2:
        adjusted_config['retry_sleep'] = 2
    
    return adjusted_config




# Cấu hình an toàn để fallback khi gặp lỗi fragment
SAFE_FALLBACK_CONFIG = {
    **DOWNLOAD_CONFIG,
    # Format đơn giản để tránh lỗi merge
    'format': 'best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'prefer_ffmpeg': False,  # Tắt ffmpeg để tránh lỗi
    
    # Cài đặt an toàn tối đa
    'concurrent_fragment_downloads': 1,  # Chỉ 1 fragment một lúc
    'buffersize': 1024,  # Buffer size nhỏ
    'http_chunk_size': 5242880,  # Chunk size 5MB
    'retries': 3,
    'fragment_retries': 5,
    'skip_unavailable_fragments': True,
    
    # Network settings an toàn
    'socket_timeout': 60,
    'extractor_retries': 3,
    
    # Không có concurrent downloads
    'max_downloads': 1,
    'max_sleep_interval': 3,
    'sleep_interval': 2,
    'max_sleep_interval_requests': 3,
    
    # Fragment handling an toàn
    'hls_prefer_native': True,
    'external_downloader': None,
    'retry_sleep': 5,
    'file_access_retries': 3,
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
