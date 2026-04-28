# Use smaller Alpine base for free tier optimization
FROM python:3.12-alpine

WORKDIR /app

# Install only essential build dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    cairo-dev \
    pkgconfig \
    && apk add --no-cache \
    cairo \
    pango \
    gdk-pixbuf \
    && rm -rf /var/cache/apk/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables for production
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV SECRET_KEY=build-phase-dummy-key-for-assets

# Collect static files during build
RUN python manage.py collectstatic --noinput

# Use gunicorn with optimized settings for free tier
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "sync", "--timeout", "30", "--max-requests", "1000", "--max-requests-jitter", "100"]
