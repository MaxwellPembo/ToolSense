#!/bin/bash
# ********************************************
# Script: server_setup.sh
# Purpose: Set up Python environment for FaceRecognizer + Azure on macOS
# ********************************************

# 1. Update brew and install system dependencies
echo "[INFO] Installing system dependencies..."
brew update
brew install cmake
brew install boost
brew install pkg-config
brew install libomp

echo "[INFO] Setting up virtual environment..."
python3 -m venv toolsense-venv
source toolsense-venv/bin/activate

echo "[INFO] Upgrading pip..."
pip install --upgrade pip

echo "[INFO] Installing required Python packages..."
pip install --upgrade wheel setuptools

pip install numpy pillow opencv-python pandas dlib face_recongition git+https://github.com/ageitgey/face_recognition_models opencv-data azure-eventhub azure-iot-device netifaces

echo "[INFO] Setup complete! Don't forget to activate your venv:"
echo "source toolsense-venv/bin/activate"
