# Stage 1: Build Frontend Assets
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Production Environment
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Install system dependencies required by OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (using PyTorch CPU wheels for lean container size)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copy backend application code and reference model assets
COPY app/ ./app
COPY models/ ./models
RUN mkdir -p uploads && chown -R appuser:appuser /app

# Copy built frontend from Stage 1
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/dist ./frontend/dist

# Switch to non-root execution
USER appuser

# Expose default port
EXPOSE 8000

# Container healthcheck probing FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run FastAPI via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
