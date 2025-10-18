FROM python:3.11-slim

# Install system dependencies (ffmpeg for audio merging)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only what’s needed first to leverage Docker caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY translate.py tts.py ./

# Default command (can be overridden in docker-compose)
CMD ["python", "translate.py"]
