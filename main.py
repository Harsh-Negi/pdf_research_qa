#!/usr/bin/env python3
"""
PDF Research Paper Q&A with Ollama - Entry point
This script launches the main application.
"""

import tkinter as tk
from pdf_research_qa.ui.app import PDFQAApp

def main():
    """Main function to start the application."""
    root = tk.Tk()
    app = PDFQAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()