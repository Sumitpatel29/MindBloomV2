#!/bin/sh
set -e
cd /app
echo "Starting Celery worker..."
celery -A mindbloom worker --loglevel=info
