web: sh -c "python manage.py runserver 0.0.0.0:80"
worker: celery -A hloot worker --loglevel=info
beat: celery -A hloot beat --loglevel=info
