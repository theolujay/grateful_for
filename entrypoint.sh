#!/bin/bash

# Exit on any error
set -e

# The first argument is the command to run, e.g., "gunicorn" or "celery".
# We run setup steps only for the main application services.
if [ "$1" = 'gunicorn' ] || [ "$1" = 'celery' ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput

    # This is safer than changing ownership of the entire project directory.
    echo "Ensuring media/staticfiles directories exist and are owned by 'app' user..."
    mkdir -p /home/app/web/staticfiles /home/app/web/media
    chown -R app:app /home/app/web/staticfiles /home/app/web/media

    echo "Running collectstatic..."
    python manage.py collectstatic --noinput
fi

echo "Executing command as 'app' user: $@"
exec gosu app "$@"
