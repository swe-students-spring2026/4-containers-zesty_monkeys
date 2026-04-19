# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY Pipfile Pipfile.lock ./

# Install pipenv + dependencies
RUN pip install pipenv && pipenv install --system --deploy

#Audio file dependencies
RUN apt-get update && apt-get install -y ffmpeg

#Uninstall CUDA from Whisper install
RUN pip uninstall -y torch torchvision torchaudio

#Replace CUDA with CPU version of PyTorch for Whisper
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy rest of project
COPY . .

# Expose port
EXPOSE 5001

# Run the server
CMD ["python", "-u", "-m", "app.server"]