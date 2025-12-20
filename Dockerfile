FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.11-slim
# Set working directory to root
WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy the entire project
COPY . .

# Ensure Python treats folders as packages
RUN touch app/__init__.py scripts/__init__.py

# Setup Permissions for the standalone cron script
RUN chmod +x /scripts/log_2fa_cron.py

# Cron Job Setup
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    echo "" >> /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Create necessary directories and log files
RUN mkdir -p /data /cron && touch /var/log/cron.log

EXPOSE 8080

# Start cron service and the FastAPI app
CMD ["sh", "-c", "service cron start && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]