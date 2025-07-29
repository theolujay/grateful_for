#!/bin/bash

# Exit on any error
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running collectstatic..."
python manage.py collectstatic --noinput

# The bind mount can result in files being owned by root.
# We change the ownership of the entire app directory to the 'app' user.
chown -R app:app /home/app/web

echo "Starting Gunicorn..."
exec gosu app gunicorn grateful_for.wsgi:application --bind 0.0.0.0:8000
