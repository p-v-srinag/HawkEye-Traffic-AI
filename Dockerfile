# Use Python 3.10 slim
FROM python:3.10-slim

WORKDIR /app

# Fix Ultralytics writable config warning and Celery root warning
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics
ENV C_FORCE_ROOT=true

# Install critical system-level dependencies for OpenCV, PaddleOCR, and YOLO-World
# (Updated to use libgl1 instead of the deprecated libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Pre-install CLIP for YOLO-World zero-shot detection
RUN pip install --no-cache-dir "git+https://github.com/ultralytics/CLIP.git"

# Copy the entire project into the container
COPY . .