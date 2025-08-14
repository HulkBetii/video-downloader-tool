# utils/system_optimizer.py
"""
Utility để tối ưu hóa system performance cho video downloader
"""

import os
import platform
import subprocess
import psutil
import threading
from typing import Dict, List, Optional

class SystemOptimizer:
    """Class để tối ưu hóa system performance"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.cpu_count = os.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        
    def get_optimal_settings(self) -> Dict:
        """Trả về cấu hình tối ưu dựa trên system specs"""
        settings = {
            'concurrent_fragment_downloads': min(20, self.cpu_count * 2),
            'max_downloads': min(3, max(1, self.cpu_count // 2)),
            'buffersize': min(8192, max(1024, int(self.memory_gb * 512))),
            'http_chunk_size': min(52428800, max(10485760, int(self.memory_gb * 10485760))),  # 10MB - 50MB
        }
        
        # Tối ưu hóa dựa trên hệ điều hành
        if self.system == 'windows':
            settings.update({
                'socket_timeout': 15,  # Windows thường có network stack tốt hơn
                'extractor_retries': 3,
            })
        elif self.system == 'darwin':  # macOS
            settings.update({
                'socket_timeout': 25,  # macOS có network stack ổn định
                'extractor_retries': 4,
            })
        else:  # Linux
            settings.update({
                'socket_timeout': 20,  # Linux có network stack linh hoạt
                'extractor_retries': 5,
            })
            
        return settings
    
    def check_external_downloaders(self) -> Dict[str, bool]:
        """Kiểm tra các external downloader có sẵn"""
        downloaders = {}
        
        # Kiểm tra aria2c
        try:
            subprocess.run(['aria2c', '--version'], capture_output=True, check=True)
            downloaders['aria2c'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            downloaders['aria2c'] = False
            
        # Kiểm tra wget
        try:
            subprocess.run(['wget', '--version'], capture_output=True, check=True)
            downloaders['wget'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            downloaders['wget'] = False
            
        # Kiểm tra curl
        try:
            subprocess.run(['curl', '--version'], capture_output=True, check=True)
            downloaders['curl'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            downloaders['curl'] = False
            
        return downloaders
    
    def get_network_optimization_tips(self) -> List[str]:
        """Trả về danh sách tips để tối ưu hóa network"""
        tips = []
        
        # Tips dựa trên system
        if self.system == 'windows':
            tips.extend([
                "🔧 Tắt Windows Defender real-time protection tạm thời",
                "🔧 Kiểm tra Windows Firewall settings",
                "🔧 Sử dụng Ethernet thay vì WiFi nếu có thể",
                "🔧 Tắt VPN nếu không cần thiết"
            ])
        elif self.system == 'darwin':
            tips.extend([
                "🔧 Kiểm tra macOS Firewall settings",
                "🔧 Tắt VPN nếu không cần thiết",
                "🔧 Sử dụng Ethernet thay vì WiFi nếu có thể"
            ])
        else:  # Linux
            tips.extend([
                "🔧 Kiểm tra iptables/firewalld settings",
                "🔧 Tối ưu hóa TCP parameters",
                "🔧 Sử dụng Ethernet thay vì WiFi nếu có thể"
            ])
            
        # Tips chung
        tips.extend([
            "🌐 Kiểm tra DNS settings (thử 8.8.8.8 hoặc 1.1.1.1)",
            "🌐 Tắt IPv6 nếu không cần thiết",
            "🌐 Kiểm tra router QoS settings",
            "🌐 Đóng các ứng dụng sử dụng nhiều bandwidth"
        ])
        
        return tips
    
    def optimize_system_for_downloads(self) -> Dict:
        """Tối ưu hóa system cho việc tải video"""
        optimizations = {}
        
        try:
            # Tối ưu hóa network buffer (chỉ trên Linux)
            if self.system == 'linux':
                try:
                    # Tăng network buffer size
                    subprocess.run(['sysctl', '-w', 'net.core.rmem_max=16777216'], check=True)
                    subprocess.run(['sysctl', '-w', 'net.core.wmem_max=16777216'], check=True)
                    optimizations['network_buffer'] = "Tăng network buffer size thành công"
                except subprocess.CalledProcessError:
                    optimizations['network_buffer'] = "Không thể tăng network buffer size (cần sudo)"
            
            # Tối ưu hóa disk I/O
            if self.system == 'windows':
                # Windows tự động tối ưu hóa
                optimizations['disk_io'] = "Windows tự động tối ưu hóa disk I/O"
            else:
                # Linux/macOS
                optimizations['disk_io'] = "Disk I/O được tối ưu hóa tự động"
                
        except Exception as e:
            optimizations['error'] = f"Lỗi khi tối ưu hóa system: {e}"
            
        return optimizations
    
    def get_performance_report(self) -> Dict:
        """Trả về báo cáo performance của system"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'count': self.cpu_count,
                    'usage_percent': cpu_percent,
                    'status': 'Good' if cpu_percent < 80 else 'High' if cpu_percent < 95 else 'Critical'
                },
                'memory': {
                    'total_gb': round(self.memory_gb, 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'usage_percent': memory.percent,
                    'status': 'Good' if memory.percent < 80 else 'High' if memory.percent < 95 else 'Critical'
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2),
                    'status': 'Good' if disk.free / disk.total > 0.1 else 'Low'
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        except Exception as e:
            return {'error': f"Không thể lấy thông tin system: {e}"}

def main():
    """Test function"""
    optimizer = SystemOptimizer()
    
    print("🔍 System Optimization Report")
    print("=" * 50)
    
    # System info
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"💻 CPU Cores: {optimizer.cpu_count}")
    print(f"💾 Memory: {optimizer.memory_gb:.1f} GB")
    
    # Optimal settings
    print("\n⚡ Optimal Settings:")
    optimal = optimizer.get_optimal_settings()
    for key, value in optimal.items():
        print(f"   {key}: {value}")
    
    # External downloaders
    print("\n🔧 External Downloaders:")
    downloaders = optimizer.check_external_downloaders()
    for name, available in downloaders.items():
        status = "✅ Available" if available else "❌ Not available"
        print(f"   {name}: {status}")
    
    # Network optimization tips
    print("\n🌐 Network Optimization Tips:")
    tips = optimizer.get_network_optimization_tips()
    for tip in tips:
        print(f"   {tip}")
    
    # Performance report
    print("\n📊 Performance Report:")
    report = optimizer.get_performance_report()
    if 'error' not in report:
        print(f"   CPU: {report['cpu']['usage_percent']}% ({report['cpu']['status']})")
        print(f"   Memory: {report['memory']['usage_percent']}% ({report['memory']['status']})")
        print(f"   Disk: {report['disk']['usage_percent']}% ({report['disk']['status']})")
    else:
        print(f"   Error: {report['error']}")

if __name__ == "__main__":
    main()
