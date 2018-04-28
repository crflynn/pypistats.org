export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
pipenv run celery -A pypistats.run.celery worker -l info
