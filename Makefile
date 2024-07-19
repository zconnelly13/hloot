DOCKER_CMD=docker exec -it $(shell docker ps | grep hloot-web | cut -d " " -f 1) python3 manage.py

# Django management commands
migrate:
	$(DOCKER_CMD) migrate

makemigrations:
	$(DOCKER_CMD) makemigrations

dbshell:
	$(DOCKER_CMD) dbshell

shell:
	$(DOCKER_CMD) shell

# Testing and linting
test:
	python3 manage.py test game

lint:
	flake8 game/ hloot/

# Game loop
gameloop:
	python3 manage.py shell < game/game_loop.py

# Frontend
fe:
	cd frontend && npm start

open:
	open "${REACT_APP_API_BASE_URL}"

# Docker build and compose
build:
	docker build --build-arg REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL} \
                 --build-arg MIDJOURNEY_API_KEY=${MIDJOURNEY_API_KEY} \
                 --build-arg DATABASE_URL=${DATABASE_URL} \
                 --build-arg DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY}" \
                 --build-arg DJANGO_DEBUG=${DJANGO_DEBUG} \
                 -t hloot .

up:
	docker-compose up

down:
	docker-compose down

restart-celery:
	docker-compose up --build -d celery

prune:
	docker system prune -a -f

# Stable diffusion
stable-diffusion:
	cd stable-diffusion-webui && ./webui.sh


# Aliases
bup: down build open up
nup: down prune build open up
sd: stable-diffusion
