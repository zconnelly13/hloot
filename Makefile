migrate:
	python3 manage.py migrate

makemigrations:
	python3 manage.py makemigrations

run:
	python3 manage.py runserver 0.0.0.0:8000

dbshell:
	python3 manage.py dbshell

shell:
	python3 manage.py shell

test:
	python3 manage.py test game

fe:
	cd frontend && npm start

gameloop:
	python3 manage.py shell < game/game_loop.py

lint:
	flake8 game/ hloot/ 

build:
	docker build --build-arg REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL} --build-arg MIDJOURNEY_API_KEY=${MIDJOURNEY_API_KEY} -t hloot .

buildnocache:
	docker build --build-arg REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL} --build-arg MIDJOURNEY_API_KEY=${MIDJOURNEY_API_KEY} -t hloot --no-cache .

down:
	docker-compose down

collectstatic:
	python3 manage.py collectstatic

up:
	docker-compose up

proxy:
	docker-compose --file docker-compose-nginx-dev.yml up --build
