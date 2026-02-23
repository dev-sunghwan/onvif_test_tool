@echo off
title ONVIF Command Tester - Build
cd /d "%~dp0"

echo ============================================
echo  ONVIF Command Tester - EXE Build
echo ============================================
echo.

REM Create/activate venv if needed
if not exist ".venv\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
pip install pyinstaller -q

echo [2/3] Building executable...
pyinstaller onvif_tester.spec --clean --noconfirm

echo.
if exist "dist\ONVIF_Command_Tester.exe" (
    echo ============================================
    echo  BUILD SUCCESS
    echo  Output: dist\ONVIF_Command_Tester.exe
    for %%A in ("dist\ONVIF_Command_Tester.exe") do echo  Size: %%~zA bytes
    echo ============================================
) else (
    echo ============================================
    echo  BUILD FAILED - check output above
    echo ============================================
)
echo.
pause
