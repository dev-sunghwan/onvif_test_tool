@echo off
echo ====================================
echo   ONVIF Command Tester
echo ====================================
echo.

cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo Starting Flask server...
echo Open browser to: http://127.0.0.1:5000
echo.
start http://127.0.0.1:5000
python app.py
