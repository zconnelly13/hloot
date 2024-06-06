web: gunicorn hloot.wsgi:application --log-file -
worker: celery -A hloot worker --beat --loglevel=info
