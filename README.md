# Expense Flow

Professional desktop software for managing visa and finance records for multiple companies.

## Features

- Company-based record management
- Dynamic visa/finance process forms
- Automatic total calculations
- MongoDB Atlas cloud database
- PDF export functionality
- Modern dark-themed UI
- Dashboard with statistics

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MongoDB:
   - Copy `.env.example` to `.env`
   - Add your MongoDB Atlas connection string

3. Run the application:
```bash
python main.py
```

## Building .exe

```bash
pyinstaller ExpenseFlow.spec
```

The executable will be in `dist/ExpenseFlow.exe`

## Project Structure

```
ExpenseFlow/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── config.py              # Configuration settings
├── database/
│   ├── __init__.py
│   ├── connection.py       # MongoDB connection
│   └── models.py          # Data models
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── sidebar.py         # Sidebar navigation
│   ├── dashboard.py       # Dashboard view
│   ├── companies.py       # Company management
│   ├── add_record.py     # Add record form
│   ├── records_view.py   # Records table view
│   └── styles.py         # UI styles and themes
├── utils/
│   ├── __init__.py
│   ├── pdf_exporter.py   # PDF generation
│   └── helpers.py        # Utility functions
└── assets/
    └── (icons and resources)
```
