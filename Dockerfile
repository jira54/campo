FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential python3-dev libcairo2-dev pkg-config && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
# Required for collectstatic during build phase
ENV SECRET_KEY=build-phase-dummy-key-for-assets
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
