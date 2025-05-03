"""
Resource Monitor Module for PDF Research Paper Q&A
Tracks system resources like CPU, RAM, and GPU usage.
"""

import threading
import time
import psutil
import platform
from typing import Dict, Any


# Try to import GPU monitoring libraries based on what's available
try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_PYNVML = True
except Exception:  # Catch any exception during import or initialization
    HAS_PYNVML = False

class ResourceMonitor:
    """Monitor system resources like CPU, RAM, and GPU usage."""
    
    def __init__(self, update_interval=1.0):
        """Initialize the resource monitor."""
        self.update_interval = update_interval
        self.monitoring = False
        self.cpu_history = []
        self.ram_history = []
        self.gpu_history = []
        self.timestamps = []
        self.start_time = None
        self.has_gpu = HAS_GPUTIL or HAS_PYNVML
        
    def start(self):
        """Start monitoring resources."""
        self.monitoring = True
        self.cpu_history = []
        self.ram_history = []
        self.gpu_history = []
        self.timestamps = []
        self.start_time = time.time()
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        
    def stop(self):
        """Stop monitoring resources."""
        self.monitoring = False
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            # Get current timestamp relative to start time
            current_time = time.time() - self.start_time
            self.timestamps.append(current_time)
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_history.append(cpu_percent)
            
            # Get RAM usage
            ram_info = psutil.virtual_memory()
            ram_percent = ram_info.percent
            self.ram_history.append(ram_percent)
            
            # Get GPU usage if available
            if HAS_GPUTIL:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu_percent = gpus[0].load * 100
                        self.gpu_history.append(gpu_percent)
                    else:
                        self.gpu_history.append(0)
                except Exception:
                    self.gpu_history.append(0)
            elif HAS_PYNVML:
                try:
                    device_count = pynvml.nvmlDeviceGetCount()
                    if device_count > 0:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        gpu_percent = utilization.gpu
                        self.gpu_history.append(gpu_percent)
                    else:
                        self.gpu_history.append(0)
                except Exception:
                    self.gpu_history.append(0)
            else:
                self.gpu_history.append(0)
                
            time.sleep(self.update_interval)
            
    def get_current_usage(self) -> Dict[str, Any]:
        """Get the current resource usage."""
        cpu_percent = psutil.cpu_percent(interval=None)
        ram_info = psutil.virtual_memory()
        ram_percent = ram_info.percent
        ram_used = ram_info.used / (1024 * 1024)  # Convert to MB
        ram_total = ram_info.total / (1024 * 1024)  # Convert to MB
        
        result = {
            "cpu_percent": cpu_percent,
            "ram_percent": ram_percent,
            "ram_used_mb": ram_used,
            "ram_total_mb": ram_total,
            "gpu_available": self.has_gpu,
            "gpu_percent": 0
        }
        
        # Get GPU info if available
        if HAS_GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    result["gpu_percent"] = gpu.load * 100
                    result["gpu_memory_used"] = gpu.memoryUsed
                    result["gpu_memory_total"] = gpu.memoryTotal
                    result["gpu_name"] = gpu.name
            except Exception as e:
                print(f"Error getting GPU info: {e}")
        elif HAS_PYNVML:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    result["gpu_percent"] = utilization.gpu
                    result["gpu_memory_used"] = memory_info.used / (1024 * 1024)  # Convert to MB
                    result["gpu_memory_total"] = memory_info.total / (1024 * 1024)  # Convert to MB
                    result["gpu_name"] = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            except Exception as e:
                print(f"Error getting GPU info: {e}")
        
        return result
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        info = {
            "os": platform.system() + " " + platform.release(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "has_gpu": self.has_gpu
        }
        
        # Add GPU info if available
        if HAS_GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    info["gpu_name"] = gpus[0].name
                    info["gpu_memory_gb"] = round(gpus[0].memoryTotal / 1024, 2)
            except Exception:
                pass
        elif HAS_PYNVML:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    info["gpu_name"] = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    info["gpu_memory_gb"] = round(memory_info.total / (1024**3), 2)
            except Exception:
                pass
        
        return info
    def update_resource_display(self):
        # Get current resource usage
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        ram_used_mb = psutil.virtual_memory().used / (1024 * 1024)
    
        # Debug print
        print(f"CPU: {cpu_percent}%, RAM: {ram_percent}%")
    
        # Update the display
        self.resource_display.update(cpu_percent, ram_percent, ram_used_mb)
    
        # Schedule the next update
        self.root.after(1000, self.update_resource_display)  # Update every second