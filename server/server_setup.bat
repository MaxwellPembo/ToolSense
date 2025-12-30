@echo off
REM ********************************************
REM Script: server_setup.bat
REM Purpose: Set up Python environment for FaceRecognizer + Azure on Windows
REM ********************************************

echo [INFO] Checking for Chocolatey...
where choco >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Chocolatey is not installed.
    echo Install it from https://chocolatey.org/install
    pause
    exit /b 1
)

echo [INFO] Installing system dependencies...
choco install -y cmake
choco install -y boost-msvc-14.3
choco install -y pkgconfiglite
choco install -y llvm

echo [INFO] Creating virtual environment...
python -m venv toolsense-venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call toolsense-venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing Python build tools...
pip install --upgrade wheel setuptools

echo [INFO] Installing required Python packages...
pip install ^
 numpy ^
 pillow ^
 opencv-python ^
 pandas ^
 azure-eventhub ^
 azure-iot-device ^
 netifaces ^
 opencv-data ^
 git+https://github.com/ageitgey/face_recognition_models

echo [INFO] Installing dlib and face_recognition...
pip install dlib face_recognition

echo [INFO] Setup complete!
echo To activate the venv later, run:
echo toolsense-venv\Scripts\activate.bat
pause
