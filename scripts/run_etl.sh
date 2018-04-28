export ENV=prod
set -o allexport
source pypistats/secret/$ENV.env
set +o allexport
pipenv run python -m pypistats.tasks.pypi
