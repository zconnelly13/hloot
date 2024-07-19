DOCKER_CMD=docker exec -it $(shell docker ps | grep hloot-web | cut -d " " -f 1) python3 manage.py

migrate:
	$(DOCKER_CMD) migrate

makemigrations:
	$(DOCKER_CMD) makemigrations

dbshell:
	$(DOCKER_CMD) dbshell

shell:
	$(DOCKER_CMD) shell

test:
	python3 manage.py test game

fe:
	cd frontend && npm start

gameloop:
	python3 manage.py shell < game/game_loop.py

lint:
	flake8 game/ hloot/ 

build:
	docker build --build-arg REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL} \
                 --build-arg MIDJOURNEY_API_KEY=${MIDJOURNEY_API_KEY} \
                 --build-arg DATABASE_URL=${DATABASE_URL} \
                 --build-arg DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY}" \
                 --build-arg DJANGO_DEBUG=${DJANGO_DEBUG} \
                 -t hloot .

down:
	docker-compose down

up:
	docker-compose up

prune:
	docker system prune -a -f

bup: down build up
nup: down prune build up

open:
	open "${REACT_APP_API_BASE_URL}"
