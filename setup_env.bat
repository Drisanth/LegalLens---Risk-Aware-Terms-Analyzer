@echo off
echo Setting up LegalLens Environment...

REM Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.9+
    pause
    exit /b 1
)

REM Create Virtual Environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate venv
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found!
    pause
    exit /b 1
)

echo Setup Complete.
echo To activate venv, run: venv\Scripts\activate
pause
