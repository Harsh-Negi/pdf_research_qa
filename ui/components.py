"""
PDF Research Paper Q&A - UI Components
This module provides reusable UI components for the PDF Research Q&A application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LabeledEntry:
    """A labeled text entry field with optional button."""
    
    def __init__(self, parent, label_text, button_text=None, button_command=None, 
                 width=30, bind_enter=None, placeholder=None):
        """
        Initialize a labeled entry component.
        
        Args:
            parent: Parent tkinter container
            label_text: Text for the label
            button_text: Optional text for a button
            button_command: Command for the button
            width: Width of the entry field
            bind_enter: Optional function to bind to Enter key
            placeholder: Optional placeholder text
        """
        self.frame = ttk.Frame(parent)
        self.label = ttk.Label(self.frame, text=label_text)
        self.label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.var = tk.StringVar()
        self.placeholder = placeholder
        
        self.entry = ttk.Entry(self.frame, textvariable=self.var, width=width)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        if placeholder:
            self.var.set(placeholder)
            self.entry.bind("<FocusIn>", self._clear_placeholder)
            self.entry.bind("<FocusOut>", self._add_placeholder)
        
        if button_text and button_command:
            self.button = ttk.Button(self.frame, text=button_text, command=button_command)
            self.button.grid(row=0, column=2, padx=5, pady=5)
        
        if bind_enter:
            self.entry.bind("<Return>", lambda e: bind_enter())
        
        self.frame.columnconfigure(1, weight=1)
    
    def _clear_placeholder(self, event):
        if self.var.get() == self.placeholder:
            self.var.set("")
    
    def _add_placeholder(self, event):
        if not self.var.get().strip():
            self.var.set(self.placeholder)
    
    def get(self):
        """Get the current value, ignoring placeholder text."""
        value = self.var.get()
        if value == self.placeholder:
            return ""
        return value
    
    def set(self, value):
        """Set the entry value."""
        self.var.set(value)
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class InfoDisplay:
    """A component to display labeled information."""
    
    def __init__(self, parent, title="Information", padding=10):
        """
        Initialize an information display component.
        
        Args:
            parent: Parent tkinter container
            title: Title for the frame
            padding: Padding inside the frame
        """
        self.frame = ttk.LabelFrame(parent, text=title, padding=padding)
        self.row = 0
        self.labels = {}
        self.values = {}
    
    def add_field(self, key, label_text, initial_value="", wraplength=300):
        """
        Add a field to the information display.
        
        Args:
            key: Unique key for this field
            label_text: Text for the label
            initial_value: Initial value to display
            wraplength: Maximum width for wrapped text
        """
        ttk.Label(self.frame, text=label_text).grid(row=self.row, column=0, sticky="nw", pady=2)
        
        value_var = tk.StringVar(value=initial_value)
        value_label = ttk.Label(self.frame, textvariable=value_var, wraplength=wraplength)
        value_label.grid(row=self.row, column=1, sticky="w", pady=2)
        
        self.labels[key] = label_text
        self.values[key] = value_var
        
        self.row += 1
    
    def update_field(self, key, value):
        """
        Update the value of a field.
        
        Args:
            key: Field key
            value: New value
        """
        if key in self.values:
            self.values[key].set(value)
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class ScrolledTextOutput:
    """A scrollable text output component with optional title."""
    
    def __init__(self, parent, title=None, height=20, width=50, readonly=True):
        """
        Initialize a scrolled text output component.
        
        Args:
            parent: Parent tkinter container
            title: Optional title
            height: Height in lines
            width: Width in characters
            readonly: Whether the text should be read-only
        """
        if title:
            self.frame = ttk.LabelFrame(parent, text=title, padding=5)
        else:
            self.frame = ttk.Frame(parent, padding=5)
        
        self.text = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, width=width, height=height)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        self.readonly = readonly
        if readonly:
            self.text.config(state=tk.DISABLED)
    
    def insert(self, text):
        """
        Insert text at the end.
        
        Args:
            text: Text to insert
        """
        if self.readonly:
            self.text.config(state=tk.NORMAL)
        
        self.text.insert(tk.END, text)
        
        if self.readonly:
            self.text.config(state=tk.DISABLED)
        
        self.text.see(tk.END)
    
    def clear(self):
        """Clear all text."""
        if self.readonly:
            self.text.config(state=tk.NORMAL)
        
        self.text.delete(1.0, tk.END)
        
        if self.readonly:
            self.text.config(state=tk.DISABLED)
    
    def get_text(self):
        """Get all text."""
        return self.text.get(1.0, tk.END)
    
    def set_text(self, text):
        """Replace all text with new content."""
        self.clear()
        self.insert(text)
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class ResourceDisplayPanel:
    """A component to display system resource usage."""
    
    def __init__(self, parent, title="Resource Usage", padding=10):
        """
        Initialize a resource display panel.
        
        Args:
            parent: Parent tkinter container
            title: Title for the frame
            padding: Padding inside the frame
        """
        self.frame = ttk.LabelFrame(parent, text=title, padding=padding)
        
        # CPU usage
        ttk.Label(self.frame, text="CPU:").grid(row=0, column=0, sticky="w")
        self.cpu_var = tk.StringVar(value="0%")
        ttk.Label(self.frame, textvariable=self.cpu_var).grid(row=0, column=1, sticky="w")
        
        # RAM usage
        ttk.Label(self.frame, text="RAM:").grid(row=1, column=0, sticky="w")
        self.ram_var = tk.StringVar(value="0%")
        ttk.Label(self.frame, textvariable=self.ram_var).grid(row=1, column=1, sticky="w")
        
        # GPU usage
        ttk.Label(self.frame, text="GPU:").grid(row=2, column=0, sticky="w")
        self.gpu_var = tk.StringVar(value="N/A")
        ttk.Label(self.frame, textvariable=self.gpu_var).grid(row=2, column=1, sticky="w")
    
    def update(self, cpu_percent, ram_percent, ram_used_mb=None, gpu_percent=None):
        """
        Update resource values.
        
        Args:
            cpu_percent: CPU usage percentage
            ram_percent: RAM usage percentage
            ram_used_mb: RAM used in MB (optional)
            gpu_percent: GPU usage percentage (optional)
        """
        self.cpu_var.set(f"{cpu_percent:.1f}%")
        
        if ram_used_mb:
            self.ram_var.set(f"{ram_percent:.1f}% ({ram_used_mb:.0f} MB)")
        else:
            self.ram_var.set(f"{ram_percent:.1f}%")
        
        if gpu_percent is not None:
            self.gpu_var.set(f"{gpu_percent:.1f}%")
        else:
            self.gpu_var.set("N/A")
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class ResourceGraphs:
    """A component to display resource usage graphs."""
    
    def __init__(self, parent, title="Resource Usage Over Time"):
        """
        Initialize resource usage graphs.
        
        Args:
            parent: Parent tkinter container
            title: Title for the frame
        """
        self.frame = ttk.LabelFrame(parent, text=title)
        
        # Create matplotlib figure with three subplots
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
        self.ax1.set_ylabel('CPU %')
        self.ax2.set_ylabel('RAM %')
        self.ax3.set_ylabel('GPU %')
        self.ax3.set_xlabel('Time (s)')
        
        # Set y-axis limits
        self.ax1.set_ylim(0, 100)
        self.ax2.set_ylim(0, 100)
        self.ax3.set_ylim(0, 100)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Initial empty data
        self.timestamps = []
        self.cpu_data = []
        self.ram_data = []
        self.gpu_data = []
    
    def update(self, timestamps, cpu_data, ram_data, gpu_data):
        """
        Update the graphs with new data.
        
        Args:
            timestamps: List of time values
            cpu_data: List of CPU percentages
            ram_data: List of RAM percentages
            gpu_data: List of GPU percentages
        """
        # Store the data
        self.timestamps = timestamps
        self.cpu_data = cpu_data
        self.ram_data = ram_data
        self.gpu_data = gpu_data
        
        # Clear the plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Set labels again
        self.ax1.set_ylabel('CPU %')
        self.ax2.set_ylabel('RAM %')
        self.ax3.set_ylabel('GPU %')
        self.ax3.set_xlabel('Time (s)')
        
        # Set y-axis limits
        self.ax1.set_ylim(0, 100)
        self.ax2.set_ylim(0, 100)
        self.ax3.set_ylim(0, 100)
        
        # Plot the data
        if timestamps:
            self.ax1.plot(timestamps, cpu_data, color='blue')
            self.ax2.plot(timestamps, ram_data, color='green')
            self.ax3.plot(timestamps, gpu_data, color='red')
        
        # Update the canvas
        self.canvas.draw()
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class StatusBar:
    """A status bar component for the bottom of the window."""
    
    def __init__(self, parent):
        """
        Initialize a status bar.
        
        Args:
            parent: Parent tkinter container
        """
        self.var = tk.StringVar()
        self.label = ttk.Label(
            parent, textvariable=self.var, relief=tk.SUNKEN, anchor=tk.W)
        # Remove this line: self.label.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        self.set("Ready")
    
    def set(self, text):
        """
        Set the status text.
        
        Args:
            text: Status text to display
        """
        self.var.set(text)
        
    def grid(self, **kwargs):
        """Grid the component."""
        self.label.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.label.pack(**kwargs)
    
    # In components.py - StatusBar class
    def set_status(self, text):
        """Alias of set() for compatibility."""
        self.set(text)


class ChatHistory:
    """A component to display Q&A chat history."""
    
    def __init__(self, parent, title="Q&A History", height=10, width=50):
        """
        Initialize a chat history component.
        
        Args:
            parent: Parent tkinter container
            title: Title for the frame
            height: Height in lines
            width: Width in characters
        """
        self.frame = ttk.LabelFrame(parent, text=title, padding=10)
        
        self.text = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, width=width, height=height)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.config(state=tk.DISABLED)
    
    def add_qa(self, question, answer):
        """
        Add a question-answer pair to the history.
        
        Args:
            question: Question text
            answer: Answer text
        """
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"\nQ: {question}\n")
        self.text.insert(tk.END, f"A: {answer}\n")
        self.text.insert(tk.END, "-" * 50 + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear the chat history."""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class ModelSelector:
    """A component for selecting models with auto-refresh capability."""
    
    def __init__(self, parent, label_text="Model:", width=28, refresh_command=None):
        """
        Initialize a model selector component.
        
        Args:
            parent: Parent tkinter container
            label_text: Text for the label
            width: Width of the combobox
            refresh_command: Command for the refresh button
        """
        self.frame = ttk.Frame(parent)
        
        ttk.Label(self.frame, text=label_text).grid(row=0, column=0, sticky="w", pady=5)
        
        self.var = tk.StringVar(value="")
        self.dropdown = ttk.Combobox(self.frame, textvariable=self.var, width=width)
        self.dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        if refresh_command:
            ttk.Button(self.frame, text="Refresh", command=refresh_command).grid(
                row=0, column=2, padx=5, pady=5)
    
    def set_values(self, values):
        """
        Set the dropdown values.
        
        Args:
            values: List of values for the dropdown
        """
        self.dropdown['values'] = values
    
    def get(self):
        """Get the selected value."""
        return self.var.get()
    
    def set(self, value):
        """Set the selected value."""
        self.var.set(value)
    
    def grid(self, **kwargs):
        """Grid the component."""
        self.frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the component."""
        self.frame.pack(**kwargs)


class ConfirmDialog:
    """A utility class for confirmation dialogs."""
    
    @staticmethod
    def ask(parent, title, message):
        """
        Show a confirmation dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message
            
        Returns:
            True if confirmed, False otherwise
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog on parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 300
        dialog_height = 120
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Dialog content
        ttk.Label(dialog, text=message, wraplength=280).pack(pady=(15, 20))
        
        result = tk.BooleanVar(value=False)
        
        def on_yes():
            result.set(True)
            dialog.destroy()
        
        def on_no():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Yes", command=on_yes).pack(side=tk.RIGHT, padx=(5, 10))
        ttk.Button(button_frame, text="No", command=on_no).pack(side=tk.RIGHT)
        
        # Wait for the dialog to close
        parent.wait_window(dialog)
        
        return result.get()