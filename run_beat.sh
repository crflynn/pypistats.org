export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
celery beat -A pypistats.run.celery -l info
