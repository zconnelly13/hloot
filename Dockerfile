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

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

# Copy application files
COPY . /app/
COPY .env /app/frontend/.env

# Build the React frontend
WORKDIR /app/frontend
RUN npm install --prefix /app/frontend
RUN npm run build --prefix /app/frontend

# Move the build files to the Django static directory
RUN mkdir -p /app/staticfiles/play/
RUN cp -r build/* /app/staticfiles/
RUN cp -r build/* /app/staticfiles/play/

# Back to the app root
WORKDIR /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Start the Django server and the continuous script loop
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000 & python game/game_loop.py"]
