fmt:
	poetry run isort -y
	poetry run black .
	terraform fmt

rebuild:
	docker-compose down
	docker-compose build
	docker-compose up

up:
	docker-compose up

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up

build:
	docker-compose build