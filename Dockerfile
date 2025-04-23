# Base image with Playwright dependencies
FROM mcr.microsoft.com/playwright/python:latest

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port for health check server
ENV PORT 8000
EXPOSE 8000

# Default command: run a simple HTTP health check
CMD ["python", "health_check.py"]