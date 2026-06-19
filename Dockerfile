# Use Python 3.10 slim
FROM python:3.10-slim

WORKDIR /app

# Install critical system-level dependencies for OpenCV and PaddleOCR
# (Updated to use libgl1 instead of the deprecated libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .