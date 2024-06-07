# Base image
FROM python:3.10

# Set build-time environment variables
ARG MIDJOURNEY_API_KEY
ARG REACT_APP_API_BASE_URL
ARG DATABASE_URL

# Set runtime environment variables
ENV MIDJOURNEY_API_KEY=$MIDJOURNEY_API_KEY
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL
ENV DATABASE_URL=$DATABASE_URL

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2

# Copy project files
COPY . /app

# Create and set permissions for the db directory
RUN mkdir -p /app/db && chown -R www-data:www-data /app/db

# Copy entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Run the web server by default
CMD ["gunicorn", "hloot.wsgi:application", "--log-file", "-"]
