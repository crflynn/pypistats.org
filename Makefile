.PHONY: fmt
fmt:
	poetry run isort -y
	poetry run black .
	terraform fmt

.PHONY: pypistats
pypistats:
	docker-compose build
	docker-compose up

.PHONY: setup
setup:
	brew install asdf
	asdf plugin add python
	asdf plugin add poetry
	asdf install
	poetry install
