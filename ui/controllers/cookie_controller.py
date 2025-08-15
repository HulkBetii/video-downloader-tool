# ui/controllers/cookie_controller.py
import os


class CookieController:
    """Controller for cookie management operations"""
    
    def __init__(self, app):
        self.app = app
    
    def restore_default_cookie_paths(self):
        """Restore default cookie paths for both video and OneDrive"""
        default_cookie_path = r"C:\Users\HH\Downloads\video_downloader_tool_donev1\video_downloader_tool\moithuvemmo-my.sharepoint.com_cookies.txt"
        
        # Restore for video download
        if os.path.exists(default_cookie_path):
            self.app.download_tab.video_cookie_input.cookie_entry.delete(0, "end")
            self.app.download_tab.video_cookie_input.cookie_entry.insert(0, default_cookie_path)
            self.app.download_tab.video_cookie_input.use_cookies.set(True)
            self.app.download_tab.video_cookie_input.cookie_entry.config(state="normal")
            self.app.download_tab.video_cookie_input.toggle_cookie_entry()
        else:
            self.app.download_tab.video_cookie_input.use_cookies.set(False)
            self.app.download_tab.video_cookie_input.cookie_entry.delete(0, "end")
            self.app.download_tab.video_cookie_input.cookie_entry.insert(0, "Cookie file không tìm thấy")
            self.app.download_tab.video_cookie_input.cookie_entry.config(state="disabled")
        
        # Restore for OneDrive download
        if os.path.exists(default_cookie_path):
            self.app.download_tab.onedrive_cookie_input.cookie_entry.delete(0, "end")
            self.app.download_tab.onedrive_cookie_input.cookie_entry.insert(0, default_cookie_path)
            self.app.download_tab.onedrive_cookie_input.use_cookies.set(True)
            self.app.download_tab.onedrive_cookie_input.cookie_entry.config(state="normal")
            self.app.download_tab.onedrive_cookie_input.toggle_cookie_entry()
        else:
            self.app.download_tab.onedrive_cookie_input.use_cookies.set(False)
            self.app.download_tab.onedrive_cookie_input.cookie_entry.delete(0, "end")
            self.app.download_tab.onedrive_cookie_input.cookie_entry.insert(0, "Cookie file không tìm thấy")
            self.app.download_tab.onedrive_cookie_input.cookie_entry.config(state="disabled")
    
    def restore_default_onedrive_cookie_paths(self):
        """Restore default cookie path for OneDrive only"""
        default_onedrive_cookie_path = r"C:\Users\HH\Downloads\video_downloader_tool_donev1\video_downloader_tool\moithuvemmo-my.sharepoint.com_cookies.txt"
        
        if os.path.exists(default_onedrive_cookie_path):
            self.app.download_tab.onedrive_cookie_input.cookie_entry.delete(0, "end")
            self.app.download_tab.onedrive_cookie_input.cookie_entry.insert(0, default_onedrive_cookie_path)
            self.app.download_tab.onedrive_cookie_input.use_cookies.set(True)
            self.app.download_tab.onedrive_cookie_input.cookie_entry.config(state="normal")
            self.app.download_tab.onedrive_cookie_input.toggle_cookie_entry()
        else:
            self.app.download_tab.onedrive_cookie_input.use_cookies.set(False)
            self.app.download_tab.onedrive_cookie_input.cookie_entry.delete(0, "end")
            self.app.download_tab.onedrive_cookie_input.cookie_entry.insert(0, "Cookie file không tìm thấy")
            self.app.download_tab.onedrive_cookie_input.cookie_entry.config(state="disabled")
    
    def initialize_cookies(self):
        """Initialize cookie state after all widgets are created"""
        try:
            # Initialize cookie for video download
            if self.app.download_tab.video_cookie_input.use_cookies.get():
                self.app.download_tab.video_cookie_input.toggle_cookie_entry()
            
            # Initialize cookie for OneDrive download
            if self.app.download_tab.onedrive_cookie_input.use_cookies.get():
                self.app.download_tab.onedrive_cookie_input.toggle_cookie_entry()
                
        except Exception as e:
            print(f"Lỗi khi khởi tạo cookie: {e}")
    
    def get_video_cookie_file(self):
        """Get video cookie file path if enabled"""
        return self.app.download_tab.video_cookie_input.get_cookie_file()
    
    def get_onedrive_cookie_file(self):
        """Get OneDrive cookie file path if enabled"""
        return self.app.download_tab.onedrive_cookie_input.get_cookie_file()
    
    def is_video_cookie_enabled(self):
        """Check if video cookie is enabled"""
        return self.app.download_tab.video_cookie_input.is_enabled()
    
    def is_onedrive_cookie_enabled(self):
        """Check if OneDrive cookie is enabled"""
        return self.app.download_tab.onedrive_cookie_input.is_enabled()
