export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
pipenv run celery beat -A pypistats.run.celery -l info
