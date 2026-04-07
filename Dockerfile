FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential python3-dev libcairo2-dev pkg-config && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
RUN python manage.py collectstatic --noinput || true
CMD ["sh", "-c", "python manage.py fix_migration && python manage.py migrate --fake-initial && python create_user.py || true && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]