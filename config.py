"""Configuration settings for Expense Flow."""
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://jamyasir0534_db_user:eUQKuhA7XJGzLbhG@cluster0.secih0o.mongodb.net/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'nasir')

# Application Settings
APP_NAME = os.getenv('APP_NAME', 'Expense Flow')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# UI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
SIDEBAR_WIDTH = 220

# Colors (Dark Theme - design.html)
COLORS = {
    # Backgrounds
    'bg': '#0e0e0e',                # Main background
    'surface': '#161616',           # Sidebar, topbar
    'card': '#1c1c1c',              # Card backgrounds
    'card2': '#212121',             # Hover states
    'bg_dark': '#0c0c0c',
    
    # Text
    'text': '#f0ede8',              # Primary text
    'text2': '#9a9590',             # Secondary text
    'text3': '#5a5752',             # Tertiary text
    'text_primary_dark': '#f0ede8',
    'text_secondary_dark': '#9a9590',
    'text_primary_light': '#f0ede8',
    'text_secondary_light': '#9a9590',
    
    # Accent (amber)
    'amber': '#d4831a',
    'amber2': '#e8962a',
    'amber_dim': '#2a1c08',
    'amber_glow': 'rgba(212,131,26,0.15)',
    'accent': '#d4831a',
    'accent_hover': '#e8962a',
    'accent_muted': 'rgba(212,131,26,0.1)',
    
    # Functional
    'green': '#2ecc71',
    'red': '#e74c3c',
    'blue': '#3b82f6',
    'success': '#2ecc71',
    'error': '#e74c3c',
    'warning': '#f59e0b',
    
    # Borders
    'border': '#2a2a2a',
    'border2': '#323232',
    'border_dark': '#2a2a2a',
    'border_light': '#2a2a2a',
    
    # Legacy compatibility
    'terminal_bg': '#0a0a0a',
    'terminal_text': '#00ff41',
    'bg_light': '#0e0e0e',
    'bg_card_light': '#1c1c1c',
    'bg_card_dark': '#1c1c1c',
}

# Available Processes
AVAILABLE_PROCESSES = [
    'Typing',
    'Labour Fees + Insurance',
    'Entry Permit',
    'Change Status',
    'Tawjeeh Class',
    'ILOE Insurance',
    'Medical + ID',
    'Stamping',
    'Renew Establishment',
    'Update Express',
    'Fine',
]

# Processes with special fields (additional inputs)
SPECIAL_PROCESSES = {
    'ILOE Insurance': {'has_fine': True, 'fine_label': 'Insurance Fine'},
    'Medical + ID': {'has_id_fee': True, 'id_fee_label': 'ID Fee'},
}

# Export Settings
EXPORT_FOLDER = 'Expense Flow'
