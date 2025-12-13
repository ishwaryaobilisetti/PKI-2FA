FROM python:3.11-slim AS builder

WORKDIR /build

COPY app/requirements.txt .
RUN pip wheel --wheel-dir=/wheels -r requirements.txt



# -----------------------
# FINAL STAGE
# -----------------------
FROM python:3.11-slim

WORKDIR /app

# Install cron + timezone
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

# Copy Python wheels from builder
COPY --from=builder /wheels /wheels
COPY app/requirements.txt /build/requirements.txt
RUN pip install --no-index --find-links=/wheels -r /build/requirements.txt

# Copy your entire app folder
COPY app /app

# Copy PEM keys (correct paths after moving them inside app/)
COPY app/student_private.pem /app/student_private.pem
COPY app/student_public.pem /app/student_public.pem
COPY app/instructor_public.pem /app/instructor_public.pem

# Copy cron job
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Correct permissions and install cron task
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# Create folders for logs and seed output
RUN mkdir -p /data /cron

# Expose API port
EXPOSE 8080

# Start cron + FastAPI server together
CMD ["sh", "-c", "service cron start && uvicorn main:app --host 0.0.0.0 --port 8080"]
