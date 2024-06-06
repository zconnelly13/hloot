#!/bin/sh

# Wait for PostgreSQL to be ready
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run database migrations
python manage.py migrate

# Collect static files (optional, if you serve static files via Django)
python manage.py collectstatic --noinput

exec "$@"
