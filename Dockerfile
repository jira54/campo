FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
RUN python manage.py collectstatic --noinput || true
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
