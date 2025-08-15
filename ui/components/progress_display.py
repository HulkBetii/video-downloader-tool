# ui/components/progress_display.py
import tkinter as tk
from tkinter import ttk


class ProgressDisplay(tk.Frame):
    """Progress display component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#f4f6fb")
        
        # Progress bar frame
        self.progress_frame = tk.Frame(self, bg="#f4f6fb")
        self.progress_frame.pack(fill="x", pady=(10, 0))
        
        # Main progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x")
        
        # Detailed progress info frame (hidden)
        self.detailed_progress_frame = tk.Frame(self, bg="#f4f6fb")
        # self.detailed_progress_frame.pack(fill="x", pady=(5, 0))  # Hidden
        
        # Fragment progress label (hidden)
        self.fragment_progress_label = tk.Label(self.detailed_progress_frame, text="", 
                                              font=("Segoe UI", 9), bg="#f4f6fb", 
                                              fg="#666", justify="left")
        # self.fragment_progress_label.pack(anchor="w")  # Hidden
        
        # Download speed and ETA label (hidden)
        self.speed_eta_label = tk.Label(self.detailed_progress_frame, text="", 
                                      font=("Segoe UI", 9), bg="#f4f6fb", 
                                      fg="#666", justify="left")
        # self.speed_eta_label.pack(anchor="w")  # Hidden
        
        # Status label
        self.status_label = tk.Label(self, text="Sẵn sàng.", fg="#3b5998", 
                                   bg="#f4f6fb", font=("Segoe UI", 10, "italic"), 
                                   wraplength=250)
        self.status_label.pack(pady=5)
    
    def start_progress(self):
        """Start the progress bar"""
        self.progress_bar.start()
    
    def stop_progress(self):
        """Stop the progress bar"""
        self.progress_bar.stop()
    
    def update_status(self, text, color="#3b5998"):
        """Update status text"""
        self.status_label.config(text=text, fg=color)
    
    def update_fragment_progress(self, text):
        """Update fragment progress text (disabled)"""
        pass
    
    def update_speed_eta(self, text):
        """Update speed and ETA text (disabled)"""
        pass
    
    def clear_progress(self):
        """Clear all progress information"""
        self.stop_progress()
    
    def parse_and_display_progress(self, status_text, line_number):
        """Parse and display detailed progress information"""
        # Disabled detailed progress display
        pass
