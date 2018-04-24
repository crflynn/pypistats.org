export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
celery -A pypistats.run.celery worker -l info
