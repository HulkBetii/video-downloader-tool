# Video Downloader Tool

Tool tải video với tối ưu hóa tốc độ và chất lượng cao.

## Tính năng

- ✅ Tải video với độ phân giải cao nhất
- ⚡ Tối ưu hóa tốc độ tải với nhiều chế độ
- 🎯 Hỗ trợ nhiều định dạng video
- 🔄 Hiển thị tiến trình tải real-time
- 🍪 Hỗ trợ cookies (.txt và .json) cho video bị giới hạn
- 🔧 Tự động phát hiện và sử dụng ffmpeg

## Cài đặt

### Yêu cầu cơ bản
```bash
pip install yt-dlp
```

### Cài đặt ffmpeg (tùy chọn - để merge video chất lượng cao)

#### Windows
1. Tải ffmpeg từ: https://ffmpeg.org/download.html
2. Giải nén và thêm vào PATH
3. Hoặc sử dụng chocolatey: `choco install ffmpeg`

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

## Sử dụng

### Chạy GUI (Khuyến nghị)
```bash
cd video_downloader_tool
python main.py
```

### Chạy command line
```bash
cd video_downloader_tool
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --out ./downloads
```

### Ví dụ CLI
```bash
# Tải một video
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --out ./downloads

# Tải nhiều video
python main.py --url "video1.mp4" "video2.mp4" --out ./downloads --mode speed

# Tải với cookie
python main.py --url "https://onedrive.live.com/..." --out ./downloads --cookie cookies.txt

# Chế độ verbose
python main.py --url "https://vimeo.com/..." --out ./downloads --verbose

# Kiểm tra ffmpeg
python main.py --check-ffmpeg
```

## Hỗ trợ Cookies

### Định dạng được hỗ trợ

#### 1. File .txt (Netscape format)
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1735689600	sessionid	your_session_id_here
.youtube.com	TRUE	/	TRUE	1735689600	LOGIN_INFO	your_login_info_here
```

#### 2. File .json
```json
[
  {
    "name": "sessionid",
    "value": "your_session_id_here",
    "domain": ".youtube.com",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "expires": 1735689600
  },
  {
    "name": "LOGIN_INFO",
    "value": "your_login_info_here",
    "domain": ".youtube.com",
    "path": "/",
    "secure": true,
    "httpOnly": false,
    "expires": 1735689600
  }
]
```

### Cách sử dụng cookies
1. Chọn "Dùng cookie file (.txt/.json)" trong GUI
2. Chọn file cookie (.txt hoặc .json)
3. Tool sẽ tự động phát hiện định dạng và sử dụng

## Chế độ tối ưu hóa

### 1. Cân bằng (Balanced)
- Số fragment đồng thời: 8
- Buffer size: 1KB
- Chunk size: 10MB
- Phù hợp cho hầu hết trường hợp

### 2. Tốc độ cao (Speed)
- Số fragment đồng thời: 16
- Buffer size: 2KB
- Chunk size: 20MB
- Tối ưu cho tốc độ tải nhanh
- **Không sử dụng ffmpeg** để tránh chậm

### 3. Chất lượng cao (Quality)
- Ưu tiên video 1080p+
- Số fragment đồng thời: 4
- Tối ưu cho chất lượng video
- **Yêu cầu ffmpeg** để merge video



## Tối ưu hóa đã thực hiện

### Tốc độ tải
- **Concurrent fragment downloads**: Tải nhiều fragment cùng lúc
- **Buffer size optimization**: Tăng buffer size để giảm I/O
- **HTTP chunk size**: Tăng chunk size để giảm overhead
- **Retry mechanism**: Tự động retry khi lỗi
- **Skip unavailable fragments**: Bỏ qua fragment không có sẵn

### Network optimization
- **Socket timeout**: Timeout hợp lý cho socket
- **Extractor retries**: Retry cho extractor
- **Error handling**: Xử lý lỗi tốt hơn

### UI improvements
- **Progress bar**: Hiển thị tiến trình tải
- **Speed display**: Hiển thị tốc độ tải real-time
- **ETA display**: Hiển thị thời gian còn lại
- **Optimization mode selection**: Chọn chế độ tối ưu hóa
- **Tab-based interface**: Giao diện với 2 tabs chính
- **System optimization tab**: Hiển thị thông tin hệ thống và tips tối ưu hóa
- **Performance monitoring**: Theo dõi hiệu suất hệ thống real-time

## 📁 **Cấu trúc Project**

```
video_downloader_tool/
├── core/                 # Logic chính của ứng dụng
│   ├── config.py        # Cấu hình download
│   └── downloader.py    # Engine download video
├── ui/                  # Giao diện người dùng
│   ├── components/      # UI components tái sử dụng
│   │   ├── url_input.py
│   │   ├── cookie_input.py
│   │   ├── optimization_selector.py
│   │   └── progress_display.py
│   ├── views/           # Main view classes
│   │   ├── main_window.py
│   │   └── download_tab.py
│   ├── controllers/     # UI event handlers
│   │   ├── download_controller.py
│   │   ├── onedrive_controller.py
│   │   └── cookie_controller.py
│   └── __init__.py
├── utils/               # Tiện ích hỗ trợ
│   ├── cookies.py       # Xử lý cookie files
│   ├── ffmpeg_checker.py # Kiểm tra ffmpeg
│   └── system_optimizer.py # Tối ưu hóa hệ thống
├── main.py              # Entry point chính (GUI + CLI)
├── cli.py               # Command-line interface
├── requirements.txt     # Dependencies
├── README.md           # Hướng dẫn sử dụng
├── COOKIE_SETUP.md     # Hướng dẫn thiết lập cookie
├── CHANGELOG.md        # Lịch sử thay đổi
├── .gitignore          # Git ignore rules
└── moithuvemmo-my.sharepoint.com_cookies.txt # Cookie file mặc định
```

## Troubleshooting

### Lỗi thường gặp
1. **Import errors**: Sử dụng `python main.py` thay vì `python run.py`
2. **"download_video" is not defined**: Kiểm tra import statement
3. **Import "ui.downloader_ui" could not be resolved**: File đã được refactor thành modular structure
4. **Tốc độ tải chậm**: Thử chế độ "Tốc độ cao"
5. **"ffmpeg is not installed"**: 
   - Tool sẽ tự động sử dụng format đơn giản
   - Hoặc cài đặt ffmpeg theo hướng dẫn trên
6. **Cookie file không hoạt động**:
   - Kiểm tra định dạng file (.txt hoặc .json)
   - Đảm bảo file có quyền đọc
   - Xem ví dụ trong thư mục `examples/`

### Yêu cầu hệ thống
- Python 3.7+
- yt-dlp
- ffmpeg (tùy chọn - cho merge video chất lượng cao)
- tkinter (cho GUI)

### Lưu ý về ffmpeg
- **Không bắt buộc**: Tool hoạt động bình thường không có ffmpeg
- **Tự động phát hiện**: Tool sẽ kiểm tra và sử dụng ffmpeg nếu có
- **Fallback**: Nếu không có ffmpeg, sẽ sử dụng format đơn giản
- **Chế độ tốc độ**: Luôn bỏ qua ffmpeg để tối ưu tốc độ

### Lưu ý về cookies
- **Hỗ trợ 2 định dạng**: .txt (Netscape) và .json
- **Tự động phát hiện**: Tool sẽ tự động nhận diện định dạng
- **Validation**: Kiểm tra tính hợp lệ của file trước khi sử dụng
- **Error handling**: Thông báo rõ ràng nếu file không hợp lệ

## 🍪 **Cookie Configuration**

Tool đã được cấu hình sẵn để sử dụng cookie file `moithuvemmo-my.sharepoint.com_cookies.txt` cho cả video download và OneDrive download.

**Cookie file location**: `C:\Users\HH\Downloads\video_downloader_tool_donev1\video_downloader_tool\moithuvemmo-my.sharepoint.com_cookies.txt`

### **Tính năng Cookie:**
- ✅ **Tự động phát hiện**: Tool tự động tìm và cấu hình cookie file
- ✅ **Mặc định bật**: Cookie được bật sẵn cho cả hai loại download
- ✅ **Nút khôi phục**: Có thể khôi phục về cài đặt mặc định
- ✅ **Hỗ trợ nhiều format**: .txt và .json files
- ✅ **Đường dẫn tuyệt đối**: Sử dụng đường dẫn cố định để đảm bảo tìm thấy file

### **Lợi ích:**
- Tải video private yêu cầu đăng nhập
- Truy cập file OneDrive/SharePoint private
- Không cần nhập username/password mỗi lần
- Bảo mật thông tin đăng nhập

Xem chi tiết trong [COOKIE_SETUP.md](COOKIE_SETUP.md)

## 🚀 **Cách sử dụng**

### Yêu cầu
- Python 3.7+
- psutil library: `pip install psutil`
- ffmpeg (cho chế độ Chất lượng cao)
- aria2c (tùy chọn, để tăng tốc độ tải)
