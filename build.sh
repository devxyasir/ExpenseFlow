#!/bin/bash
# Build script for Expense Flow - macOS/Linux

echo "========================================"
echo "   Expense Flow - Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip3 install -r requirements.txt || exit 1

echo ""
echo "[2/4] Installing PyInstaller..."
pip3 install pyinstaller || exit 1

echo ""
echo "[3/4] Building executable (this may take a few minutes)..."
pyinstaller --clean ExpenseFlow.onefile.spec || exit 1

echo ""
echo "[4/4] Build complete!"
echo ""
echo "========================================"
echo "   Output: dist/ExpenseFlow"
echo "========================================"
echo ""
echo "IMPORTANT: Before running the application:"
echo "1. Copy .env.example to .env"
echo "2. Add your MongoDB Atlas connection string to .env"
echo ""
