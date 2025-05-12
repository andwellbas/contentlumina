# Base image with Python
FROM python:3.10-slim

# Disable Python caching and enable logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the code into the container
COPY . .

# Collect static files and start the Gunicorn server on port 8000
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn contentlumina.wsgi:application --bind 0.0.0.0:8000"]