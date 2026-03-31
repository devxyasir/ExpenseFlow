@echo off
REM Build script for Expense Flow - Windows

echo ========================================
echo    Expense Flow - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo [2/4] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    exit /b 1
)

echo.
echo [3/4] Building executable (this may take a few minutes)...
pyinstaller --clean ExpenseFlow.onefile.spec
if errorlevel 1 (
    echo ERROR: Build failed
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo ========================================
echo    Output: dist\ExpenseFlow.exe
echo ========================================
echo.
echo IMPORTANT: Before running the application:
echo 1. Copy .env.example to .env
echo 2. Add your MongoDB Atlas connection string to .env
echo.
pause
