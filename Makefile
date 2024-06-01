run:
	docker-compose up

build:
	docker-compose up --build

server-up:
	docker start work_server

server-down:
	docker stop work_server

server-shell:
	docker exec -it work_server /bin/bash

test: server-up
	docker exec -it work_server pytest --cov-fail-under=99
	docker stop work_server

lint:
	docker exec -it work_server isort .
	docker exec -it work_server black .
	docker exec -it work_server flake8 --exit-zero

all: test lint