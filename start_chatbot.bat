@echo off
echo ========================================
echo    Wonk Chatbot Startup Script
echo ========================================
echo.

if not exist "app.py" (
    echo ERROR: app.py not found. Please run from project directory.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please check Python installation
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -q flask

echo.
echo Starting Wonk Chatbot...
echo Visit: http://localhost:5000
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py

echo.
echo Wonk Chatbot has stopped
pause
