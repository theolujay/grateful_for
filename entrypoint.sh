#!/bin/bash

# Exit on any error
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn grateful_for.wsgi:application --bind 0.0.0.0:8000
