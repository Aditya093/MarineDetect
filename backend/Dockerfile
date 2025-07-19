# Backend Dockerfile
FROM python:3.9.6-slim

# Set working directory
WORKDIR /app

# Install system dependencies and download tools
RUN apt-get update && \
    apt-get install -y curl ca-certificates libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Download and install uv (latest Linux x86_64 binary)
# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"
RUN uv venv
ENV UV_HTTP_TIMEOUT=480
# Copy and install Python dependencies using uv
COPY requirements.txt ./
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY app/ app/
COPY models/ models/
COPY utils/ utils/

# Expose port
EXPOSE 8000

# Start the FastAPI app
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

