#!/bin/bash
# Face Recognition Setup Script for Raspberry Pi (Debian 13 / Trixie)
# Installs Python 3.11, venv, cmake, and Python packages for face recognition

set -e

echo "=== Updating system packages ==="
sudo apt update
sudo apt upgrade -y

echo "=== Installing essential build tools ==="
sudo apt install -y build-essential cmake git \
    libblas-dev liblapack-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libx11-dev libgtk-3-dev \
    python3-venv python3-pip python3-dev

# Check if Python 3.11 is installed
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
if [[ $PYTHON_VERSION != 3.11* ]]; then
    echo "=== Installing Python 3.11 from source ==="
    sudo apt install -y libffi-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev tk-dev llvm libncurses5-dev libncursesw5-dev xz-utils

    mkdir -p ~/src
    cd ~/src
    wget https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz
    tar xvf Python-3.11.8.tgz
    cd Python-3.11.8
    ./configure --enable-optimizations --with-ensurepip=install
    make -j$(nproc)
    sudo make altinstall
    cd ~
    echo "Python 3.11 installed."
else
    echo "Python 3.11 is already installed."
fi

# Create a virtual environment
echo "=== Creating virtual environment toolsense-venv ==="
python3.11 -m venv ~/toolsense-venv

echo "=== Activating virtual environment ==="
source ~/toolsense-venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

echo "=== Installing Python packages ==="
pip install cmake dlib face_recognition opencv-python opencv-data netifaces azure-iot-device time json

echo "=== Setup complete ==="
echo "Activate your virtual environment with:"
echo "  source ~/toolsense-venv/bin/activate"