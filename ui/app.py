"""
Main application window for PDF Research Q&A.
"""

import tkinter as tk
from tkinter import ttk
import platform

from .main_tab import MainTab
from .logging_tab import LoggingTab
from .components import StatusBar


class PDFQAApp:
    """Main application window for PDF Research Paper Q&A."""
    
    def __init__(self, root):
        """Initialize the application UI.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("PDF Research Paper Q&A with Session Logging")
        self.root.geometry("1200x800")
        
        # Set theme based on platform
        if platform.system() == "Windows":
            style = ttk.Style()
            style.theme_use("vista")
        
        # Configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=1, column=0, sticky="ew")
        
        # Initialize tabs
        self.main_tab = MainTab(self.notebook, self.status_bar)
        self.logging_tab = LoggingTab(self.notebook, self.status_bar)
        
        # Add tabs to notebook
        self.notebook.add(self.main_tab, text="PDF Q&A")
        self.notebook.add(self.logging_tab, text="Session Log")
        
        # Set up communication between tabs
        self.main_tab.set_logger(self.logging_tab.logger)
        self.logging_tab.set_resource_monitor(self.main_tab.resource_monitor)
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Handle tab change events."""
        current_tab = self.notebook.select()
        if current_tab == self.notebook.tabs()[1]:  # Logging tab
            self.logging_tab.refresh_log()
            self.logging_tab.update_resource_graphs()
            
    def run(self):
        """Start the main application loop."""
        self.root.mainloop()