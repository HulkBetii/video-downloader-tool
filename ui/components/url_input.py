# ui/components/url_input.py
import tkinter as tk
from tkinter import ttk


class URLInput(tk.Frame):
    """Reusable URL input component with line numbers"""
    
    def __init__(self, parent, label_text="🔗 URL:", **kwargs):
        super().__init__(parent, bg="#f4f6fb")
        
        # Label
        tk.Label(self, text=label_text, font=("Segoe UI", 11, "bold"), bg="#f4f6fb").pack(anchor="w")
        
        # Input frame
        input_frame = tk.Frame(self, bg="#f4f6fb")
        input_frame.pack(fill="x", pady=(5, 0))
        
        # Line numbers frame (left side)
        self.line_numbers = tk.Text(input_frame, width=4, height=3, font=("Consolas", 10), 
                                   bg="#f0f0f0", relief="sunken", bd=1, state="disabled")
        self.line_numbers.pack(side="left", fill="y")
        
        # URL input frame (right side)
        self.url_entry = tk.Text(input_frame, width=40, height=3, font=("Segoe UI", 11), 
                                relief="groove", bd=2, wrap="none")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Scrollbar for URL input
        url_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.url_entry.yview)
        self.url_entry.configure(yscrollcommand=url_scrollbar.set)
        url_scrollbar.pack(side="right", fill="y")
        
        # Bind events
        self.url_entry.bind('<Key>', self.update_line_numbers)
        self.url_entry.bind('<KeyRelease>', self.update_line_numbers)
        self.url_entry.bind('<Button-1>', self.update_line_numbers)
        self.url_entry.bind('<KeyRelease>', self.highlight_current_line)
        
        # Initialize line numbers
        self.update_line_numbers()
    
    def update_line_numbers(self, event=None):
        """Update line numbers display"""
        try:
            content = self.url_entry.get("1.0", tk.END)
            lines = content.split('\n')
            
            line_numbers_text = ""
            for i in range(1, len(lines) + 1):
                line_numbers_text += f"{i}\n"
            
            self.line_numbers.config(state="normal")
            self.line_numbers.delete("1.0", tk.END)
            self.line_numbers.insert("1.0", line_numbers_text)
            self.line_numbers.config(state="disabled")
        except Exception:
            pass
    
    def highlight_current_line(self, event):
        """Highlight current line in line numbers"""
        try:
            current_line = self.url_entry.index(tk.INSERT).split('.')[0]
            self.line_numbers.tag_remove("current_line", "1.0", tk.END)
            self.line_numbers.tag_add("current_line", f"{current_line}.0", f"{current_line}.end")
            self.line_numbers.tag_config("current_line", background="#e3e6f0")
        except Exception:
            pass
    
    def get_urls(self):
        """Get list of URLs from the input"""
        content = self.url_entry.get("1.0", tk.END).strip()
        if not content:
            return []
        
        urls = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
        
        return urls
    
    def set_urls(self, urls):
        """Set URLs in the input"""
        self.url_entry.delete("1.0", tk.END)
        if urls:
            self.url_entry.insert("1.0", '\n'.join(urls))
        self.update_line_numbers()
    
    def clear(self):
        """Clear the input"""
        self.url_entry.delete("1.0", tk.END)
        self.update_line_numbers()
