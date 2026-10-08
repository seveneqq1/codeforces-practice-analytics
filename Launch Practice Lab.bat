@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 is required. Install it from https://python.org and try again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 (
    echo Could not create the Python environment.
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m pip install --disable-pip-version-check --quiet -r requirements.txt
if errorlevel 1 (
    echo Could not install the required packages.
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m streamlit run app.py
