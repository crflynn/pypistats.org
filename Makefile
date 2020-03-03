PYPISTATS_WEB_CONTAINER=pypistatsorg_web_1

# format everything
.PHONY: fmt
fmt:
	poetry run isort -y
	poetry run black .
	terraform fmt

# launch the application in docker-compose
.PHONY: pypistats
pypistats:
	docker-compose build
	docker-compose up

# setup a local environment
.PHONY: setup
setup:
	brew install asdf
	asdf install
	poetry install

# create a migration
# ensure the app is running in compose
# run with `make migration MIGRATION_NAME=my_migration_name`
.PHONY: migration
migration:
	docker exec -it $(PYPISTATS_WEB_CONTAINER) poetry run flask db migrate -m "$(MIGRATION_NAME)"
