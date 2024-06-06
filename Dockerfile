# Base image
FROM python:3.10

# Set build-time environment variables
ARG MIDJOURNEY_API_KEY
ARG REACT_APP_API_BASE_URL

# Set runtime environment variables
ENV MIDJOURNEY_API_KEY=$MIDJOURNEY_API_KEY
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Back to the app root
WORKDIR /app

# Run migrations
RUN python manage.py migrate

# Start the Django server and the continuous script loop
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
