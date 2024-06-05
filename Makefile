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
	docker build . -t hloot

collectstatic:
	python3 manage.py collectstatic

up:
	docker-compose up --build
