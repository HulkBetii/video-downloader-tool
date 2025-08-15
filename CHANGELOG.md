# Changelog - Video Downloader Tool

## [1.3.0] - 2024-01-XX

### 🧹 Project Cleanup
- **Dọn dẹp project**: Xóa các file và thư mục không cần thiết
- **Loại bỏ tài liệu tạm thời**: Xóa `UI_IMPROVEMENTS.md` (thông tin đã tích hợp vào CHANGELOG)
- **Loại bỏ ví dụ không cần thiết**: Xóa `examples/cookies_example.json` và thư mục `examples/`
- **Tối ưu hóa cấu trúc**: Loại bỏ `__init__.py` không cần thiết cho project standalone

### 📁 Files Removed
- `UI_IMPROVEMENTS.md` - Tài liệu UI improvements tạm thời
- `examples/cookies_example.json` - File ví dụ cookie không cần thiết
- `examples/` - Thư mục ví dụ trống
- `__init__.py` - File khởi tạo package không cần thiết

## [1.2.0] - 2024-01-XX

### 🍪 Added
- **Cookie mặc định**: Tự động chọn file `moithuvemmo-my.sharepoint.com_cookies.txt`
- **Tự động phát hiện**: Tool tự động tìm và cấu hình cookie file
- **Nút khôi phục**: Thêm nút "🔄 Mặc định" để khôi phục cài đặt cookie
- **Cookie documentation**: Tạo file `COOKIE_SETUP.md` hướng dẫn chi tiết

### 🔧 Improved
- **Cookie state management**: Cải thiện việc quản lý trạng thái cookie
- **Error handling**: Xử lý tốt hơn khi cookie file không tồn tại
- **User experience**: Cookie được bật mặc định cho cả video và OneDrive
- **Cookie initialization**: Sửa lỗi cookie checkbox không được khởi tạo đúng trạng thái

### 🐛 Fixed
- **Cookie UI state**: Sửa lỗi cookie checkbox được bật nhưng input field vẫn bị khóa
- **Initialization order**: Đảm bảo cookie được khởi tạo sau khi tất cả widgets được tạo
- **Toggle functions**: Cập nhật UI state khi khôi phục cookie mặc định
- **Cookie file path**: Sửa đường dẫn cookie file từ relative path sang absolute path để đảm bảo tìm thấy file

### 📁 Files Added
- `COOKIE_SETUP.md` - Hướng dẫn thiết lập và sử dụng cookie

## [1.1.0] - 2024-01-XX

### 🐛 Fixed
- **Lỗi file không tìm thấy**: Sửa lỗi "No such file or directory" khi tải video với nhiều fragment
- **Cải thiện xử lý lỗi**: Thêm thông báo lỗi chi tiết và gợi ý khắc phục
- **Cơ chế retry tự động**: Tự động thử lại khi gặp lỗi file với cài đặt an toàn hơn

### ⚡ Performance
- **Giảm concurrent fragment downloads**: Từ 20 xuống 8 để tránh lỗi file
- **Tối ưu hóa cấu hình**: Loại bỏ external downloader gây lỗi
- **Cải thiện quản lý file tạm thời**: Giữ file tạm thời để có thể tiếp tục download

### 🔧 Technical Improvements
- **Cấu hình download an toàn hơn**: Giảm số fragment đồng thời để ổn định
- **Xử lý lỗi nâng cao**: Phân loại và xử lý các loại lỗi khác nhau
- **Retry mechanism**: Tự động thử lại với cài đặt giảm dần khi gặp lỗi

### 📝 Configuration Changes

- `concurrent_fragment_downloads`: Giảm từ 16 xuống 6 (speed mode)  
- `concurrent_fragment_downloads`: Giảm từ 8 xuống 4 (balanced mode)
- `concurrent_fragment_downloads`: Giảm từ 4 xuống 3 (quality mode)
- Loại bỏ `external_downloader` và `external_downloader_args`
- Thêm `nopart: False`, `updatetime: False`, `writethumbnail: False`

### 🧪 Testing
- Thêm file test `test_download.py` để kiểm tra chức năng download
- Cải thiện error handling và logging

## [1.0.0] - 2024-01-XX

### ✨ Features
- Video downloader với giao diện Tkinter
- Hỗ trợ nhiều nền tảng video (YouTube, Vimeo, etc.)
- Tối ưu hóa tốc độ và chất lượng
- Hỗ trợ cookies cho video private
- Tải file từ OneDrive/SharePoint
- Giao diện đa ngôn ngữ (Tiếng Việt)
