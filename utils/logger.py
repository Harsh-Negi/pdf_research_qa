"""
Logger Module for PDF Research Paper Q&A
Handles session logging and export functionality.
"""

import os
import datetime
from typing import Dict, List, Any

from ..core.resource_monitor import ResourceMonitor  # If importing from another file in the same directory

class Logger:
    """Logs session information, queries, and resource usage."""
    
    def __init__(self):
        """Initialize the logger."""
        self.log_entries = []
        self.resource_monitor = ResourceMonitor()
        self.start_time = datetime.datetime.now()
        
        # Log session start
        self.log_session_start()
    
    def log_session_start(self):
        """Log the start of a session with system information."""
        system_info = self.resource_monitor.get_system_info()
        
        entry = {
            "timestamp": datetime.datetime.now(),
            "type": "SESSION_START",
            "system_info": system_info
        }
        
        self.log_entries.append(entry)
    
    def log_pdf_load(self, pdf_path, model, embedding_model, processing_time, title, authors):
        """Log when a PDF is loaded and processed."""
        resource_usage = self.resource_monitor.get_current_usage()
        
        entry = {
            "timestamp": datetime.datetime.now(),
            "type": "PDF_LOAD",
            "pdf_path": pdf_path,
            "model": model,
            "embedding_model": embedding_model,
            "processing_time": processing_time,
            "title": title,
            "authors": authors,
            "resource_usage": resource_usage
        }
        
        self.log_entries.append(entry)
    
    def log_query(self, question, answer, model, query_time):
        """Log a query and its answer."""
        resource_usage = self.resource_monitor.get_current_usage()
        
        entry = {
            "timestamp": datetime.datetime.now(),
            "type": "QUERY",
            "question": question,
            "answer": answer,
            "model": model,
            "query_time": query_time,
            "resource_usage": resource_usage
        }
        
        self.log_entries.append(entry)
    
    def log_error(self, operation, error_message):
        """Log an error that occurred."""
        entry = {
            "timestamp": datetime.datetime.now(),
            "type": "ERROR",
            "operation": operation,
            "error_message": error_message
        }
        
        self.log_entries.append(entry)
    
    def get_formatted_log(self):
        """Get formatted log text suitable for display or export."""
        log_text = f"=== PDF Q&A SESSION LOG ===\n"
        log_text += f"Session started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Format each log entry
        for entry in self.log_entries:
            timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            log_text += f"[{timestamp}] {entry['type']}\n"
            
            if entry["type"] == "SESSION_START":
                system_info = entry.get("system_info", {})
                log_text += f"  System: {system_info.get('os', 'Unknown OS')}\n"
                log_text += f"  CPU: {system_info.get('processor', 'Unknown')} ({system_info.get('physical_cpu_count', 0)} cores, {system_info.get('cpu_count', 0)} threads)\n"
                log_text += f"  RAM: {system_info.get('ram_total_gb', 0):.2f} GB\n"
                
                if system_info.get("has_gpu", False):
                    log_text += f"  GPU: {system_info.get('gpu_name', 'Available')}"
                    if "gpu_memory_gb" in system_info:
                        log_text += f" ({system_info['gpu_memory_gb']} GB)\n"
                    else:
                        log_text += "\n"
                else:
                    log_text += "  GPU: Not detected\n"
                    
            elif entry["type"] == "PDF_LOAD":
                log_text += f"  File: {os.path.basename(entry.get('pdf_path', 'Unknown'))}\n"
                log_text += f"  Title: {entry.get('title', 'Unknown')}\n"
                log_text += f"  Model: {entry.get('model', 'Unknown')}\n"
                log_text += f"  Embedding: {entry.get('embedding_model', 'Unknown')}\n"
                log_text += f"  Processing time: {entry.get('processing_time', 0):.2f} seconds\n"
                
                # Add resource usage
                resource_usage = entry.get("resource_usage", {})
                log_text += f"  CPU: {resource_usage.get('cpu_percent', 0):.1f}%, "
                log_text += f"RAM: {resource_usage.get('ram_percent', 0):.1f}%, "
                
                if resource_usage.get("gpu_available", False):
                    log_text += f"GPU: {resource_usage.get('gpu_percent', 0):.1f}%\n"
                else:
                    log_text += "GPU: N/A\n"
                    
            elif entry["type"] == "QUERY":
                log_text += f"  Model: {entry.get('model', 'Unknown')}\n"
                log_text += f"  Question: {entry.get('question', 'Unknown')}\n"
                log_text += f"  Query time: {entry.get('query_time', 0):.2f} seconds\n"
                
                # Add resource usage
                resource_usage = entry.get("resource_usage", {})
                log_text += f"  CPU: {resource_usage.get('cpu_percent', 0):.1f}%, "
                log_text += f"RAM: {resource_usage.get('ram_percent', 0):.1f}%, "
                
                if resource_usage.get("gpu_available", False):
                    log_text += f"GPU: {resource_usage.get('gpu_percent', 0):.1f}%\n"
                else:
                    log_text += "GPU: N/A\n"
                
                # Add answer (with indentation for readability)
                answer_lines = entry.get("answer", "No answer").split("\n")
                log_text += "  Answer:\n"
                for line in answer_lines:
                    log_text += f"    {line}\n"
                    
            elif entry["type"] == "ERROR":
                log_text += f"  Operation: {entry.get('operation', 'Unknown')}\n"
                log_text += f"  Error: {entry.get('error_message', 'Unknown error')}\n"
            
            log_text += "\n"  # Add empty line between entries
            
        return log_text
    
    def export_log(self, file_path):
        """Export the log to a file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.get_formatted_log())
            return True
        except Exception as e:
            print(f"Error exporting log: {e}")
            return False