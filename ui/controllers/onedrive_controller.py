# ui/controllers/onedrive_controller.py
import threading
import os
import sys
import requests
import re
from urllib.parse import urlparse, parse_qs

# Add the project root to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from utils.cookies import load_cookies_from_file
except ImportError:
    # Fallback for when running as script
    utils_dir = os.path.join(project_root, 'utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    try:
        from cookies import load_cookies_from_file  # type: ignore
    except ImportError:
        print("Error: Could not import required modules")
        sys.exit(1)


class OneDriveController:
    """Controller for OneDrive/SharePoint download operations"""
    
    def __init__(self, app):
        self.app = app
        self.active_downloads = 0
    
    def start_onedrive_download(self):
        """Start OneDrive download process"""
        # Get URLs from input
        urls = self.app.download_tab.onedrive_url_input.get_urls()
        if not urls:
            self.app.download_tab.onedrive_progress.update_status("❌ Vui lòng nhập URL OneDrive/SharePoint.", "red")
            return
        
        # Get output folder
        output_folder = self.app.download_tab.output_entry.get().strip()
        if not output_folder or not os.path.isdir(output_folder):
            self.app.download_tab.onedrive_progress.update_status("❌ Vui lòng chọn thư mục lưu hợp lệ.", "red")
            return
        
        # Get cookie file
        cookie_file = self.app.download_tab.onedrive_cookie_input.get_cookie_file()
        
        # Start download for each URL
        for i, url in enumerate(urls, 1):
            if url.strip():
                self.run_onedrive_download(url, output_folder, cookie_file, i)
    
    def run_onedrive_download(self, onedrive_url, output_folder, cookie_file, line_number):
        """Run OneDrive download in separate thread"""
        def update_status(status_text, color="#e67e22"):
            self.app.download_tab.onedrive_progress.update_status(status_text, color)
        
        def download_thread():
            try:
                self.active_downloads += 1
                self.app.download_tab.onedrive_download_button.config(state="disabled")
                self.app.download_tab.onedrive_progress.start_progress()
                
                update_status(f"🚀 Bắt đầu tải file OneDrive {line_number}...", "blue")
                
                # Call the download function
                success = self.download_onedrive_file(
                    onedrive_url, output_folder, cookie_file, update_status
                )
                
                if success:
                    update_status(f"✅ Hoàn tất tải file OneDrive {line_number}!", "green")
                else:
                    update_status(f"❌ Lỗi tải file OneDrive {line_number}.", "red")
                    
            except Exception as e:
                update_status(f"❌ Lỗi không xác định: {str(e)}", "red")
            finally:
                self.active_downloads -= 1
                if self.active_downloads <= 0:
                    self.app.download_tab.onedrive_download_button.config(state="normal")
                    self.app.download_tab.onedrive_progress.stop_progress()
        
        # Start download thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def download_onedrive_file(self, onedrive_url, output_folder, cookie_file, status_callback):
        """Download file from OneDrive/SharePoint"""
        try:
            # Validate URL first
            if not self.is_valid_download_url(onedrive_url):
                status_callback("❌ URL không hợp lệ hoặc không phải file có thể tải", "red")
                return False
            
            # Load cookies if provided
            cookies = {}
            if cookie_file:
                cookies = load_cookies_from_file(cookie_file)
            
            # Create session with cookies
            session = requests.Session()
            if cookies:
                session.cookies.update(cookies)
            
            # Set headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            session.headers.update(headers)
            
            status_callback("🔍 Đang phân tích URL...", "blue")
            
            # Check if it's a OneDrive/SharePoint URL
            if self.is_onedrive_url(onedrive_url):
                status_callback("✅ Xác nhận URL OneDrive/SharePoint", "green")
                
                # Handle complex SharePoint URLs
                if self.is_complex_sharepoint_url(onedrive_url):
                    return self.handle_complex_sharepoint(onedrive_url, output_folder, cookie_file, status_callback)
                else:
                    # Simple OneDrive URL
                    return self.download_from_url(onedrive_url, output_folder, None, session, status_callback)
            else:
                status_callback("⚠️ URL không phải OneDrive/SharePoint, thử tải trực tiếp...", "orange")
                return self.download_from_url(onedrive_url, output_folder, None, session, status_callback)
                
        except Exception as e:
            status_callback(f"❌ Lỗi: {str(e)}", "red")
            return False
    
    def is_onedrive_url(self, url):
        """Check if URL is OneDrive/SharePoint"""
        onedrive_domains = [
            'onedrive.live.com',
            'sharepoint.com',
            'office.com',
            'microsoft.com'
        ]
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Filter out SharePoint system pages and throttle pages
        if 'sharepoint.com' in domain:
            # Skip system pages, throttle pages, and other non-file URLs
            skip_patterns = [
                '/_layouts/15/Throttle.htm',
                '/_layouts/15/error.aspx',
                '/_layouts/15/accessdenied.aspx',
                '/_layouts/15/login.aspx',
                '/_layouts/15/',
                '/_vti_bin/',
                '/_api/',
                '/_forms/',
                '/_catalogs/',
                '/_cts/',
                '/_private/',
                '/_vti_pvt/',
                '/_vti_cnf/',
                '/_vti_log/',
                '/_vti_script/',
                '/_vti_txt/',
                '/_vti_aut/',
                '/_vti_map/',
                '/_vti_rtf/',
                '/_vti_pcn/',
                '/_vti_adm/',
                '/_vti_opt/',
                '/_vti_bin/',
                '/_vti_txt/',
                '/_vti_aut/',
                '/_vti_map/',
                '/_vti_rtf/',
                '/_vti_pcn/',
                '/_vti_adm/',
                '/_vti_opt/'
            ]
            
            for pattern in skip_patterns:
                if pattern in url.lower():
                    return False
        
        return any(domain in onedrive_domain for onedrive_domain in onedrive_domains)
    
    def is_valid_download_url(self, url):
        """Check if URL is a valid download URL (not a system page)"""
        try:
            # Basic URL validation
            if not url or not url.strip():
                return False
            
            # Check for common file extensions
            file_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.rar', '.7z', '.tar', '.gz',
                '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wmv',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp',
                '.txt', '.rtf', '.csv'
            ]
            
            url_lower = url.lower()
            
            # If URL has a file extension, it's likely valid
            if any(ext in url_lower for ext in file_extensions):
                return True
            
            # For SharePoint URLs, check if they're not system pages
            if 'sharepoint.com' in url_lower:
                # Skip system pages and throttle pages
                system_patterns = [
                    '/_layouts/15/Throttle.htm',
                    '/_layouts/15/error.aspx',
                    '/_layouts/15/accessdenied.aspx',
                    '/_layouts/15/login.aspx',
                    '/_layouts/15/',
                    '/_vti_bin/',
                    '/_api/',
                    '/_forms/',
                    '/_catalogs/',
                    '/_cts/',
                    '/_private/',
                    '/_vti_pvt/',
                    '/_vti_cnf/',
                    '/_vti_log/',
                    '/_vti_script/',
                    '/_vti_txt/',
                    '/_vti_aut/',
                    '/_vti_map/',
                    '/_vti_rtf/',
                    '/_vti_pcn/',
                    '/_vti_adm/',
                    '/_vti_opt/'
                ]
                
                for pattern in system_patterns:
                    if pattern in url_lower:
                        return False
            
            # For OneDrive URLs, they're usually valid
            if 'onedrive.live.com' in url_lower:
                return True
            
            return True  # Assume valid if no obvious issues
            
        except Exception:
            return False
    
    def is_complex_sharepoint_url(self, url):
        """Check if URL is a complex SharePoint sharing URL"""
        return 'sharepoint.com' in url.lower() and ('/personal/' in url or '/sites/' in url)
    
    def handle_complex_sharepoint(self, url, output_folder, cookie_file, status_callback):
        """Handle complex SharePoint URLs"""
        try:
            status_callback("🔧 Xử lý URL SharePoint phức tạp...", "blue")
            
            # Try multiple approaches
            approaches = [
                self.try_graph_api_download,
                self.try_page_parsing_download,
                self.try_url_manipulation_download
            ]
            
            for approach in approaches:
                try:
                    status_callback(f"🔄 Thử phương pháp: {approach.__name__}...", "blue")
                    if approach(url, output_folder, None, None, status_callback):
                        return True
                except Exception as e:
                    status_callback(f"⚠️ Phương pháp {approach.__name__} thất bại: {str(e)}", "orange")
                    continue
            
            status_callback("❌ Tất cả phương pháp đều thất bại", "red")
            return False
            
        except Exception as e:
            status_callback(f"❌ Lỗi xử lý SharePoint: {str(e)}", "red")
            return False
    
    def try_graph_api_download(self, sharing_url, output_folder, filename, session, status_callback):
        """Try Graph API approach"""
        # Simplified implementation - would need full Graph API integration
        return False
    
    def try_page_parsing_download(self, sharing_url, output_folder, filename, session, status_callback):
        """Try page parsing approach"""
        try:
            status_callback("📄 Đang phân tích trang web...", "blue")
            
            response = session.get(sharing_url, timeout=30)
            if response.status_code == 200:
                # Look for download links in the page
                download_links = self.find_download_link(response.text, sharing_url)
                if download_links:
                    for link in download_links:
                        if self.download_from_url(link, output_folder, filename, session, status_callback):
                            return True
            
            return False
        except Exception as e:
            status_callback(f"❌ Lỗi phân tích trang: {str(e)}", "red")
            return False
    
    def try_url_manipulation_download(self, sharing_url, output_folder, filename, session, status_callback):
        """Try URL manipulation approach"""
        try:
            # Try to convert sharing URL to direct download URL
            direct_url = self.convert_sharepoint_sharing_url(sharing_url)
            if direct_url:
                return self.download_from_url(direct_url, output_folder, filename, session, status_callback)
            return False
        except Exception as e:
            status_callback(f"❌ Lỗi chuyển đổi URL: {str(e)}", "red")
            return False
    
    def find_download_link(self, html_content, base_url):
        """Find download links in HTML content"""
        links = []
        # Look for common download link patterns
        patterns = [
            r'href=["\']([^"\']*\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|mp[34]|avi|mkv))["\']',
            r'href=["\']([^"\']*download[^"\']*)["\']',
            r'href=["\']([^"\']*_layouts/15/download[^"\']*)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    links.append(match)
                else:
                    # Make relative URL absolute
                    links.append(base_url.rstrip('/') + '/' + match.lstrip('/'))
        
        return links
    
    def convert_sharepoint_sharing_url(self, sharing_url):
        """Convert SharePoint sharing URL to direct download URL"""
        try:
            # Extract file ID from sharing URL
            parsed = urlparse(sharing_url)
            path_parts = parsed.path.split('/')
            
            # Look for file ID in path
            for i, part in enumerate(path_parts):
                if len(part) > 20:  # Likely a file ID
                    # Try to construct direct download URL
                    direct_url = f"https://{parsed.netloc}/_layouts/15/download.aspx?SourceUrl={sharing_url}"
                    return direct_url
            
            return None
        except Exception:
            return None
    
    def download_from_url(self, url, output_folder, filename, session, status_callback):
        """Download file from direct URL"""
        try:
            status_callback("📥 Đang tải file...", "blue")
            
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get filename from response headers or URL
            if not filename:
                content_disposition = response.headers.get('content-disposition')
                if content_disposition:
                    filename_match = re.search(r'filename=["\']([^"\']+)["\']', content_disposition)
                    if filename_match:
                        filename = filename_match.group(1)
                
                if not filename:
                    filename = url.split('/')[-1].split('?')[0]
                    if not filename or '.' not in filename:
                        filename = 'downloaded_file'
            
            file_path = os.path.join(output_folder, filename)
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            status_callback(f"📥 Đang tải: {progress:.1f}% ({downloaded}/{total_size} bytes)", "blue")
            
            status_callback(f"✅ Tải thành công: {filename}", "green")
            return True
            
        except Exception as e:
            status_callback(f"❌ Lỗi tải file: {str(e)}", "red")
            return False
    
    def get_active_downloads(self):
        """Get number of active downloads"""
        return self.active_downloads
