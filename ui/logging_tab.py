"""
Logging tab for displaying and exporting session logs.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..utils.logger import Logger


class LoggingTab(ttk.Frame):
    """Tab for displaying session logs and resource usage graphs."""
    
    def __init__(self, parent, status_bar):
        """Initialize the logging tab.
        
        Args:
            parent: Parent widget
            status_bar: Status bar for showing messages
        """
        super().__init__(parent, padding=10)
        self.status_bar = status_bar
        self.logger = Logger()
        self.resource_monitor = None
        
        # Create the UI
        self.create_ui()
    
    def set_resource_monitor(self, resource_monitor):
        """Set the resource monitor for this tab."""
        self.resource_monitor = resource_monitor
    
    def create_ui(self):
        """Create the user interface for the logging tab."""
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        
        # Create log display and controls section
        self.create_log_section()
        
        # Create resource usage graphs section
        self.create_graph_section()
    
    def create_log_section(self):
        """Create the log display and controls section."""
        log_frame = ttk.LabelFrame(self, text="Session Log")
        log_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Control buttons
        button_frame = ttk.Frame(log_frame)
        button_frame.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Refresh Log", command=self.refresh_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Log", command=self.export_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
    
    def create_graph_section(self):
        """Create the resource usage graphs section."""
        graph_frame = ttk.LabelFrame(self, text="Resource Usage Over Time")
        graph_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
        self.ax1.set_ylabel('CPU %')
        self.ax2.set_ylabel('RAM %')
        self.ax3.set_ylabel('GPU %')
        self.ax3.set_xlabel('Time (s)')
        
        # Add the plot to the tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add a refresh button for the graphs
        ttk.Button(graph_frame, text="Refresh Graphs", command=self.update_resource_graphs).pack(anchor=tk.W, padx=5, pady=5)
    
    def refresh_log(self):
        """Refresh the log display."""
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, self.logger.get_formatted_log())
        self.log_text.see(tk.END)
        self.status_bar.set_status("Log refreshed")
    
    def export_log(self):
        """Export the session log to a file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Session Log",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            if self.logger.export_log(file_path):
                messagebox.showinfo("Success", f"Log exported to {file_path}")
                self.status_bar.set_status(f"Log exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export log")
    
    def clear_log(self):
        """Clear the session log display."""
        if messagebox.askyesno("Confirm", "This will clear the current session log display. Continue?"):
            self.log_text.delete(1.0, tk.END)
            self.status_bar.set_status("Log display cleared")
    
    def update_resource_graphs(self):
        """Update the resource usage graphs with current data."""
        if not self.resource_monitor:
            return
            
        try:
            # Clear the axes
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            
            # Set labels
            self.ax1.set_ylabel('CPU %')
            self.ax2.set_ylabel('RAM %')
            self.ax3.set_ylabel('GPU %')
            self.ax3.set_xlabel('Time (s)')
            
            # Plot the data
            if self.resource_monitor.timestamps:
                self.ax1.plot(self.resource_monitor.timestamps, self.resource_monitor.cpu_history, color='blue')
                self.ax2.plot(self.resource_monitor.timestamps, self.resource_monitor.ram_history, color='green')
                self.ax3.plot(self.resource_monitor.timestamps, self.resource_monitor.gpu_history, color='red')
                
                # Set y-axis limits
                self.ax1.set_ylim(0, 100)
                self.ax2.set_ylim(0, 100)
                self.ax3.set_ylim(0, 100)
            
            # Add grid for better readability
            self.ax1.grid(True, linestyle='--', alpha=0.7)
            self.ax2.grid(True, linestyle='--', alpha=0.7)
            self.ax3.grid(True, linestyle='--', alpha=0.7)
                
            # Update the canvas
            self.canvas.draw()
            self.status_bar.set_status("Resource graphs updated")
            
        except Exception as e:
            print(f"Error updating resource graphs: {e}")
            self.status_bar.set_status(f"Error updating graphs: {e}")