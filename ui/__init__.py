"""
UI package for PDF Research Q&A application.
Contains the main UI components and application windows.
"""

from .app import PDFQAApp
from .components import StatusBar, ResourceDisplayPanel, InfoDisplay
__all__ = ['PDFQAApp', 'StatusBar', 'ResourceDisplay', 'DocumentInfoDisplay']