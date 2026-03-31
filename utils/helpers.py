"""Utility functions for Expense Flow."""
import os
from pathlib import Path
from config import EXPORT_FOLDER


def get_export_directory():
    """Get the export directory path (Desktop/Expense Flow)."""
    desktop = Path.home() / "Desktop"
    export_dir = desktop / EXPORT_FOLDER
    
    # Create if doesn't exist
    export_dir.mkdir(parents=True, exist_ok=True)
    
    return export_dir


def format_currency(amount):
    """Format amount as currency string."""
    return f"AED {amount:,.2f}"


def sanitize_filename(filename):
    """Sanitize filename for safe file system usage."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
