#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
