@echo off
REM Browser Fingerprinting Platform - Windows Development Setup Script
REM This script sets up the development environment for the BFP project on Windows

echo.
echo ================================================================================================
echo 🚀 Setting up Browser Fingerprinting Platform Development Environment (Windows)
echo ================================================================================================
echo.

REM Function to check if Python is installed
:CHECK_PYTHON
echo [STEP] Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python %PYTHON_VERSION% found ✓
echo.

REM Create virtual environment
:SETUP_VENV
echo [STEP] Setting up Python virtual environment...
if not exist "bfp" (
    python -m venv bfp
    echo [INFO] Virtual environment created ✓
) else (
    echo [INFO] Virtual environment already exists ✓
)
echo.

REM Activate virtual environment and install dependencies
:INSTALL_DEPS
echo [STEP] Installing Python dependencies...
call bfp\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install production dependencies
pip install -r requirements.txt

REM Install development dependencies if available
if exist "requirements-dev.txt" (
    pip install -r requirements-dev.txt
    echo [INFO] Development dependencies installed ✓
)

echo [INFO] Dependencies installed ✓
echo.

REM Setup environment file
:SETUP_ENV
echo [STEP] Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo [INFO] Environment file created from template ✓
    echo [WARNING] Please edit .env file with your configuration
) else (
    echo [INFO] Environment file already exists ✓
)
echo.

REM Create necessary directories
:CREATE_DIRS
echo [STEP] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "backups" mkdir backups
echo [INFO] Directories created ✓
echo.

REM Test the installation
:TEST_INSTALL
echo [STEP] Testing installation...
python -c "import fastapi, motor, redis, pydantic; print('✓ All required packages imported successfully')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Package import test failed
    pause
    exit /b 1
)
echo [INFO] Installation test passed ✓
echo.

REM Success message
echo ================================================================================================
echo 🎉 Development environment setup complete!
echo ================================================================================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Start MongoDB and Redis services
echo 3. Activate virtual environment:
echo    bfp\Scripts\activate.bat
echo 4. Run the application:
echo    uvicorn main:app --reload
echo 5. Visit http://localhost:8000 in your browser
echo.
echo For more information, see README.md
echo.

REM Check for MongoDB
echo [INFO] Checking for MongoDB...
where mongosh >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] MongoDB client found ✓
) else (
    echo [WARNING] MongoDB client not found
    echo Install MongoDB Community Edition from: https://www.mongodb.com/try/download/community
)

REM Check for Redis
echo [INFO] Checking for Redis...
where redis-cli >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Redis client found ✓
) else (
    echo [WARNING] Redis client not found
    echo Install Redis from: https://redis.io/download
    echo For Windows, you can use: https://github.com/microsoftarchive/redis/releases
)

echo.
echo Setup complete! Press any key to exit...
pause >nul
