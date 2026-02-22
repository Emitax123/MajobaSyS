# Dockerfile for MajobaSyS Django Application
# Railway deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=majobacore.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements/production.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p logs static media

# Collect static files (now works without DB/Redis variables)
RUN python manage.py collectstatic --noinput --settings=majobacore.settings.production

# Expose default port (Railway usará PORT dinámico en runtime)
EXPOSE 8000

# Default command - Railway override con railway.json startCommand
# IMPORTANTE: No usar sintaxis exec form ["cmd"] porque no expande variables
# Usar shell form para que $PORT se expanda correctamente
CMD gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
