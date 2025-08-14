# main.py
import sys
import os


# Thêm thư mục hiện tại vào đường dẫn để có thể import các mô-đun của chúng ta
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from ui.download_ui import VideoDownloaderApp
except ImportError as e:
    print(f"Lỗi khi import VideoDownloaderApp: {e}")
    print("Hãy đảm bảo rằng bạn đang chạy tập tin này từ thư mục video_downloader_tool")
    sys.exit(1)

def main():
    # Khởi chạy giao diện chính
    try:
        app = VideoDownloaderApp()
        app.mainloop()
    except Exception as e:
        print(f"Lỗi khi khởi động ứng dụng: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
