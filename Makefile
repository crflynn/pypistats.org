# format everything
fmt:
	poetry run isort .
	poetry run black .

# launch the application in docker-compose
.PHONY: pypistats
pypistats:
	docker-compose down
	docker-compose build
	docker-compose up

# bring down the application and destroy the db volumes
cleanup:
	docker-compose down -v

# setup a local environment
setup:
	brew install asdf || true
	asdf install
	poetry install

# deploy to gke
deploy:
	sh kubernetes/deploy.sh

# port forward flower
pfflower:
	open http://localhost:7777 && kubectl get pods -n pypistats | grep flower | awk '{print $$1}' | xargs -I % kubectl port-forward % 7777:5555

# port forward web
pfweb:
	open http://localhost:7000 && kubectl get pods -n pypistats | grep web | awk '{print $$1}' | xargs -I % kubectl port-forward % 7000:5000
