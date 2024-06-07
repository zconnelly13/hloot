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

# Export environment variables
export DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
export DATABASE_URL=${DATABASE_URL}
export MIDJOURNEY_API_KEY=${MIDJOURNEY_API_KEY}
export REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}
export DJANGO_DEBUG=${DJANGO_DEBUG}

# Print environment variables for debugging
echo "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
echo "DATABASE_URL=$DATABASE_URL"
echo "MIDJOURNEY_API_KEY=$MIDJOURNEY_API_KEY"
echo "REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL"
echo "DJANGO_DEBUG=$DJANGO_DEBUG"

# Run database migrations
python manage.py migrate

# Collect static files (optional, if you serve static files via Django)
python manage.py collectstatic --noinput

exec "$@"
