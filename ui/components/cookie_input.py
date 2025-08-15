# ui/components/cookie_input.py
import tkinter as tk
import os


class CookieInput(tk.Frame):
    """Reusable cookie input component"""
    
    def __init__(self, parent, label_text="Dùng cookie file (.txt/.json)", 
                 default_path=None, button_color="#3b5998", **kwargs):
        super().__init__(parent, bg="#f4f6fb")
        
        # Cookie checkbox
        self.use_cookies = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text=label_text, variable=self.use_cookies, 
                      command=self.toggle_cookie_entry, font=("Segoe UI", 10), 
                      bg="#f4f6fb").pack(anchor="w", pady=(5, 0))
        
        # Cookie input frame
        self.cookie_frame = tk.Frame(self, bg="#f4f6fb")
        self.cookie_frame.pack(fill="x", pady=(5, 10))
        
        # Cookie entry
        self.cookie_entry = tk.Entry(self.cookie_frame, font=("Segoe UI", 10), 
                                   relief="groove", bd=2)
        self.cookie_entry.pack(side="left", fill="x", expand=True, ipady=4)
        
        # Cookie button
        self.cookie_btn = tk.Button(self.cookie_frame, text="Chọn...", 
                                  command=self.select_cookie_file, 
                                  font=("Segoe UI", 10, "bold"), 
                                  bg=button_color, fg="white", 
                                  activebackground="#5b7bd5", 
                                  activeforeground="white", 
                                  relief="flat", bd=0)
        self.cookie_btn.pack(side="left", padx=8)
        
        # Restore default button
        self.restore_btn = tk.Button(self.cookie_frame, text="🔄 Mặc định", 
                                   command=self.restore_default_path, 
                                   font=("Segoe UI", 9), 
                                   bg="#6c757d", fg="white", 
                                   activebackground="#5a6268", 
                                   activeforeground="white", 
                                   relief="flat", bd=0)
        self.restore_btn.pack(side="left", padx=4)
        
        # Set default path if provided
        if default_path and os.path.exists(default_path):
            self.cookie_entry.insert(0, default_path)
        else:
            self.cookie_entry.insert(0, "Cookie file không tìm thấy")
            self.use_cookies.set(False)
            self.cookie_entry.config(state="disabled")
        
        # Initialize state
        self.toggle_cookie_entry()
    
    def toggle_cookie_entry(self):
        """Toggle cookie entry enabled/disabled state"""
        if self.use_cookies.get():
            self.cookie_entry.config(state="normal")
        else:
            self.cookie_entry.config(state="disabled")
    
    def select_cookie_file(self):
        """Open file dialog to select cookie file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Chọn file cookie",
            filetypes=[
                ("Cookie files", "*.txt;*.json"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, file_path)
            self.use_cookies.set(True)
            self.toggle_cookie_entry()
    
    def restore_default_path(self):
        """Restore default cookie path"""
        default_path = r"C:\Users\HH\Downloads\video_downloader_tool_donev1\video_downloader_tool\moithuvemmo-my.sharepoint.com_cookies.txt"
        
        if os.path.exists(default_path):
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, default_path)
            self.use_cookies.set(True)
            self.cookie_entry.config(state="normal")
            self.toggle_cookie_entry()
        else:
            self.use_cookies.set(False)
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, "Cookie file không tìm thấy")
            self.cookie_entry.config(state="disabled")
    
    def get_cookie_file(self):
        """Get cookie file path if enabled"""
        if self.use_cookies.get():
            path = self.cookie_entry.get().strip()
            if path and os.path.exists(path):
                return path
        return None
    
    def is_enabled(self):
        """Check if cookie input is enabled"""
        return self.use_cookies.get()
