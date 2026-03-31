"""Expense Flow - Desktop Application Entry Point
Standalone desktop app using Eel + HTML/JS (appears as native application)
"""
import sys
import os

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import eel first
import eel

# Import the API to register exposed functions
import eel_api
from database.connection import DatabaseConnection
from config import APP_NAME

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def start_app():
    """Start the Eel application."""
    web_dir = resource_path('web')
    
    print(f"Starting Eel desktop app from: {web_dir}")
    
    # Initialize Eel with the web folder
    eel.init(web_dir)
    
    # Start as desktop application using Chrome mode
    # Security flags: disable DevTools, extensions, and right-click context menu
    eel.start('index.html', 
              mode='chrome', 
              port=8081, 
              host='127.0.0.1',
              size=(1400, 900),
              position=(50, 50),
              cmdline_args=[
                  '--app=http://localhost:8081/index.html',
                  '--disable-features=VizDisplayCompositor,DevTools,TranslateUI',
                  '--disable-extensions',
                  '--disable-component-extensions-with-background-pages',
                  '--disable-background-networking',
                  '--disable-sync',
                  '--disable-default-apps',
                  '--no-first-run',
                  '--no-default-browser-check',
                  '--window-position=50,50',
                  '--window-size=1400,900',
                  '--force-device-scale-factor=1',
              ])

def main():
    """Main application entry point."""
    print(f"Starting {APP_NAME}...")
    
    # Initialize database connection
    db = DatabaseConnection()
    connected = db.connect()
    
    if not connected:
        print("WARNING: Could not connect to MongoDB. Running in demo mode.")
    else:
        print(f"Connected to MongoDB: {db.get_database().name}")
    
    # Start the app
    try:
        start_app()
    except Exception as e:
        print(f"Failed to start: {e}")
        print("Trying fallback mode...")
        try:
            web_dir = resource_path('web')
            eel.init(web_dir)
            eel.start('index.html', mode='default', host='localhost', port=0)
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            input("Press Enter to exit...")

if __name__ == '__main__':
    main()
