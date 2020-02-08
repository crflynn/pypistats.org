.PHONY: pypistats

fmt:
	poetry run isort -y
	poetry run black .
	terraform fmt

pypistats:
	docker-compose build
	docker-compose up

setup:
	brew install asdf
	asdf plugin add python
	asdf plugin add poetry
	asdf install python 3.7.5
	asdf install poetry 1.0.3
	poetry install
