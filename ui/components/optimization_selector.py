# ui/components/optimization_selector.py
import tkinter as tk


class OptimizationSelector(tk.Frame):
    """Optimization mode selector component"""
    
    def __init__(self, parent, ffmpeg_available=True, **kwargs):
        super().__init__(parent, bg="#f4f6fb")
        
        # Label
        tk.Label(self, text="⚡ Chế độ tối ưu hóa:", font=("Segoe UI", 11, "bold"), 
                bg="#f4f6fb").pack(anchor="w", pady=(10, 0))
        
        # Optimization mode variable
        self.optimize_mode = tk.StringVar(value="quality")
        
        # Optimization frame
        optimize_frame = tk.Frame(self, bg="#f4f6fb")
        optimize_frame.pack(fill="x", pady=(0, 10))
        
        # Style for radio buttons
        style = {"font": ("Segoe UI", 9), "bg": "#f4f6fb"}
        
        # Radio buttons
        tk.Radiobutton(optimize_frame, text="Cân bằng", variable=self.optimize_mode, 
                      value="balanced", selectcolor="#e3e6f0", **style).pack(anchor="w", pady=2)
        
        tk.Radiobutton(optimize_frame, text="Tốc độ cao", variable=self.optimize_mode, 
                      value="speed", selectcolor="#e3e6f0", **style).pack(anchor="w", pady=2)
        
        self.rb_quality = tk.Radiobutton(optimize_frame, text="Chất lượng cao", 
                                       variable=self.optimize_mode, value="quality", 
                                       selectcolor="#e3e6f0", **style)
        self.rb_quality.pack(anchor="w", pady=2)
        

        
        # Disable ffmpeg-dependent modes if ffmpeg not available
        if not ffmpeg_available:
            self.rb_quality.config(state="disabled")
            tk.Label(self, text="⚠️ ffmpeg chưa được cài đặt. Chế độ chất lượng cao đã bị vô hiệu.", 
                    font=("Segoe UI", 9), bg="#f4f6fb", fg="#ff9800").pack(anchor="w", pady=(0, 5))
            
            # Fallback selection if default was quality
            if self.optimize_mode.get() in ("quality"):
                self.optimize_mode.set("balanced")
    
    def get_mode(self):
        """Get selected optimization mode"""
        return self.optimize_mode.get()
    
    def set_mode(self, mode):
        """Set optimization mode"""
        self.optimize_mode.set(mode)
    
    def is_ffmpeg_required(self):
        """Check if current mode requires ffmpeg"""
        mode = self.optimize_mode.get()
        return mode in ("quality")
